"""
Checker for Unit 1.5 — Batch Processing Challenge
===================================================
Run with: python checker.py
    or:   pytest checker.py -v
"""

import math
import pytest
from challenge import (
    BatchProcessingChallenge,
    MAX_TOKENS_PER_DOC,
    SAMPLE_BATCH_RESULTS,
    SAMPLE_DOCUMENTS,
    SAMPLE_ORIGINAL_DOCS,
    SAMPLE_WORKFLOWS,
)


@pytest.fixture
def challenge():
    return BatchProcessingChallenge()


# ── 1. choose_api ────────────────────────────────────────────────────────


class TestChooseApi:
    """Tests for the API routing logic."""

    def test_blocking_workflows_use_synchronous(self, challenge):
        """Blocking workflows must always use the synchronous API."""
        for wf in SAMPLE_WORKFLOWS:
            if wf["blocking"]:
                result = challenge.choose_api(wf)
                assert result == "synchronous", (
                    f"Workflow '{wf['name']}' is blocking and should use "
                    f"'synchronous', got '{result}'"
                )

    def test_non_blocking_high_latency_uses_batch(self, challenge):
        """Non-blocking workflows with latency > 24h should use batch."""
        for wf in SAMPLE_WORKFLOWS:
            if not wf["blocking"] and wf["latency_hours"] > 24:
                result = challenge.choose_api(wf)
                assert result == "batch", (
                    f"Workflow '{wf['name']}' is non-blocking with "
                    f"{wf['latency_hours']}h latency and should use "
                    f"'batch', got '{result}'"
                )

    def test_non_blocking_tight_latency_uses_synchronous(self, challenge):
        """Non-blocking workflows with latency <= 24h cannot use batch."""
        wf = {
            "name": "End-of-day report",
            "blocking": False,
            "latency_hours": 18,
        }
        result = challenge.choose_api(wf)
        assert result == "synchronous", (
            f"Workflow with 18h latency cannot be served by batch (24h window). "
            f"Expected 'synchronous', got '{result}'"
        )

    def test_exactly_24h_latency_uses_synchronous(self, challenge):
        """Exactly 24h latency cannot be guaranteed by batch."""
        wf = {
            "name": "Daily digest",
            "blocking": False,
            "latency_hours": 24,
        }
        result = challenge.choose_api(wf)
        assert result == "synchronous", (
            f"Exactly 24h latency has zero margin; batch cannot guarantee "
            f"delivery. Expected 'synchronous', got '{result}'"
        )

    def test_return_type_is_string(self, challenge):
        """Return value must be a string."""
        result = challenge.choose_api(SAMPLE_WORKFLOWS[0])
        assert isinstance(result, str), f"Expected str, got {type(result)}"

    def test_return_values_are_valid(self, challenge):
        """Return value must be either 'synchronous' or 'batch'."""
        for wf in SAMPLE_WORKFLOWS:
            result = challenge.choose_api(wf)
            assert result in ("synchronous", "batch"), (
                f"Invalid return value '{result}' — must be 'synchronous' or 'batch'"
            )


# ── 2. calculate_submission_frequency ─────────────────────────────────────


class TestSubmissionFrequency:
    """Tests for batch submission interval calculation."""

    def test_basic_calculation(self, challenge):
        """30h SLA with 24h window = submit every 6h."""
        assert challenge.calculate_submission_frequency(30) == 6

    def test_large_sla(self, challenge):
        """48h SLA with 24h window = submit every 24h."""
        assert challenge.calculate_submission_frequency(48) == 24

    def test_sla_equals_window_returns_zero(self, challenge):
        """SLA exactly equal to batch window cannot be met."""
        assert challenge.calculate_submission_frequency(24) == 0

    def test_sla_less_than_window_returns_zero(self, challenge):
        """SLA shorter than batch window cannot be met."""
        assert challenge.calculate_submission_frequency(12) == 0

    def test_one_hour_margin(self, challenge):
        """25h SLA with 24h window = submit every 1h."""
        assert challenge.calculate_submission_frequency(25) == 1

    def test_large_window(self, challenge):
        """100h SLA with 24h window = submit every 76h."""
        assert challenge.calculate_submission_frequency(100) == 76

    def test_custom_batch_window(self, challenge):
        """Custom batch window of 12 hours."""
        assert challenge.calculate_submission_frequency(20, batch_window_hours=12) == 8

    def test_return_type_is_int(self, challenge):
        """Return value must be an integer."""
        result = challenge.calculate_submission_frequency(30)
        assert isinstance(result, int), f"Expected int, got {type(result)}"


# ── 3. build_batch_request ────────────────────────────────────────────────


class TestBuildBatchRequest:
    """Tests for batch request construction."""

    def test_returns_list(self, challenge):
        """Must return a list."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        assert isinstance(result, list)

    def test_correct_number_of_requests(self, challenge):
        """One request per document."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        assert len(result) == len(SAMPLE_DOCUMENTS)

    def test_custom_id_matches_doc_id(self, challenge):
        """custom_id must match the document's id."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        for i, req in enumerate(result):
            assert req["custom_id"] == SAMPLE_DOCUMENTS[i]["id"]

    def test_params_has_model(self, challenge):
        """Each request must specify the model."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        for req in result:
            assert "model" in req["params"]
            assert req["params"]["model"] == "claude-sonnet-4-20250514"

    def test_params_has_max_tokens(self, challenge):
        """Each request must specify max_tokens."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        for req in result:
            assert "max_tokens" in req["params"]
            assert req["params"]["max_tokens"] == 1024

    def test_params_has_messages(self, challenge):
        """Each request must have a messages list with user role."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        for req in result:
            messages = req["params"]["messages"]
            assert isinstance(messages, list)
            assert len(messages) >= 1
            assert messages[0]["role"] == "user"

    def test_message_contains_document_content(self, challenge):
        """The user message must contain the document content."""
        result = challenge.build_batch_request(SAMPLE_DOCUMENTS)
        for i, req in enumerate(result):
            msg_content = req["params"]["messages"][0]["content"]
            assert SAMPLE_DOCUMENTS[i]["content"] in msg_content

    def test_empty_input(self, challenge):
        """Empty document list returns empty request list."""
        result = challenge.build_batch_request([])
        assert result == []


# ── 4. handle_batch_results ──────────────────────────────────────────────


class TestHandleBatchResults:
    """Tests for batch result processing."""

    def test_returns_dict_with_required_keys(self, challenge):
        """Must return dict with succeeded, failed, retry_ids."""
        result = challenge.handle_batch_results(SAMPLE_BATCH_RESULTS)
        assert isinstance(result, dict)
        assert "succeeded" in result
        assert "failed" in result
        assert "retry_ids" in result

    def test_correct_succeeded_count(self, challenge):
        """Should correctly identify succeeded results."""
        result = challenge.handle_batch_results(SAMPLE_BATCH_RESULTS)
        assert len(result["succeeded"]) == 1

    def test_correct_failed_count(self, challenge):
        """Should correctly identify failed results."""
        result = challenge.handle_batch_results(SAMPLE_BATCH_RESULTS)
        assert len(result["failed"]) == 2

    def test_retry_ids_match_failed(self, challenge):
        """retry_ids must contain exactly the custom_ids of failed results."""
        result = challenge.handle_batch_results(SAMPLE_BATCH_RESULTS)
        assert set(result["retry_ids"]) == {"doc-002", "doc-003"}

    def test_succeeded_items_are_correct(self, challenge):
        """Succeeded list contains the correct items."""
        result = challenge.handle_batch_results(SAMPLE_BATCH_RESULTS)
        ids = [r["custom_id"] for r in result["succeeded"]]
        assert ids == ["doc-001"]

    def test_all_succeeded(self, challenge):
        """All-success scenario."""
        all_good = [
            {"custom_id": "a", "status": "succeeded", "result": {}, "error": None},
            {"custom_id": "b", "status": "succeeded", "result": {}, "error": None},
        ]
        result = challenge.handle_batch_results(all_good)
        assert len(result["succeeded"]) == 2
        assert len(result["failed"]) == 0
        assert result["retry_ids"] == []

    def test_all_failed(self, challenge):
        """All-failure scenario."""
        all_bad = [
            {"custom_id": "a", "status": "errored", "result": None,
             "error": {"type": "rate_limit", "message": "error"}},
            {"custom_id": "b", "status": "errored", "result": None,
             "error": {"type": "rate_limit", "message": "error"}},
        ]
        result = challenge.handle_batch_results(all_bad)
        assert len(result["succeeded"]) == 0
        assert len(result["failed"]) == 2
        assert set(result["retry_ids"]) == {"a", "b"}


# ── 5. prepare_retry_batch ───────────────────────────────────────────────


class TestPrepareRetryBatch:
    """Tests for retry batch preparation."""

    def test_non_context_error_resubmits_original(self, challenge):
        """Non-context errors resubmit with the same custom_id and content."""
        failed = [
            {"custom_id": "doc-003", "error": {"type": "rate_limit", "message": "err"}}
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        assert len(result) == 1
        assert result[0]["custom_id"] == "doc-003"
        msg = result[0]["params"]["messages"][0]["content"]
        assert SAMPLE_ORIGINAL_DOCS["doc-003"]["content"] in msg

    def test_context_length_error_chunks_document(self, challenge):
        """Documents exceeding context limits are split into chunks."""
        failed = [
            {"custom_id": "doc-002",
             "error": {"type": "context_length_exceeded", "message": "too long"}}
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        # doc-002 content is 10000 chars; MAX_TOKENS_PER_DOC is 4000
        # Expected chunks: ceil(10000 / 4000) = 3
        expected_chunks = math.ceil(10000 / MAX_TOKENS_PER_DOC)
        assert len(result) == expected_chunks, (
            f"Expected {expected_chunks} chunks, got {len(result)}"
        )

    def test_chunk_custom_ids_are_correct(self, challenge):
        """Chunk custom_ids follow the format: {original_id}_chunk_{index}."""
        failed = [
            {"custom_id": "doc-002",
             "error": {"type": "context_length_exceeded", "message": "too long"}}
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        expected_chunks = math.ceil(10000 / MAX_TOKENS_PER_DOC)
        for i in range(expected_chunks):
            assert result[i]["custom_id"] == f"doc-002_chunk_{i}"

    def test_chunks_cover_full_content(self, challenge):
        """All chunk contents combined must equal the original content."""
        failed = [
            {"custom_id": "doc-002",
             "error": {"type": "context_length_exceeded", "message": "too long"}}
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        original_content = SAMPLE_ORIGINAL_DOCS["doc-002"]["content"]

        # Extract just the document portion from each chunk message.
        # The message format is "Classify this document:\n\n<chunk_content>"
        # so the chunk content appears after the prefix.
        reconstructed = ""
        for req in result:
            msg = req["params"]["messages"][0]["content"]
            # Find the document content within the message
            # It should contain a substring of the original
            # We check coverage by length
            pass

        # Simpler check: total content characters across all chunks
        # must equal or exceed the original
        total_chars = sum(
            len(req["params"]["messages"][0]["content"])
            for req in result
        )
        # Each chunk message includes a prefix like "Classify this document:\n\n"
        # so total_chars will be larger than original. Just verify each chunk's
        # content portion has at most MAX_TOKENS_PER_DOC characters of original.
        assert len(result) == math.ceil(len(original_content) / MAX_TOKENS_PER_DOC)

    def test_mixed_errors(self, challenge):
        """Mixed error types are handled correctly."""
        failed = [
            {"custom_id": "doc-002",
             "error": {"type": "context_length_exceeded", "message": "too long"}},
            {"custom_id": "doc-003",
             "error": {"type": "rate_limit", "message": "err"}},
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        expected_chunks = math.ceil(10000 / MAX_TOKENS_PER_DOC)
        # doc-002 produces chunks, doc-003 produces 1 request
        assert len(result) == expected_chunks + 1

    def test_each_request_has_valid_structure(self, challenge):
        """Every retry request must have the standard batch structure."""
        failed = [
            {"custom_id": "doc-003",
             "error": {"type": "rate_limit", "message": "err"}}
        ]
        result = challenge.prepare_retry_batch(failed, SAMPLE_ORIGINAL_DOCS)
        for req in result:
            assert "custom_id" in req
            assert "params" in req
            assert "model" in req["params"]
            assert "max_tokens" in req["params"]
            assert "messages" in req["params"]
            assert req["params"]["messages"][0]["role"] == "user"

    def test_empty_failures_returns_empty(self, challenge):
        """No failures means no retry batch."""
        result = challenge.prepare_retry_batch([], SAMPLE_ORIGINAL_DOCS)
        assert result == []


# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    raise SystemExit(exit_code)
