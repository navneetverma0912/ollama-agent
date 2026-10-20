import unittest
from types import SimpleNamespace
from uuid import UUID, uuid4
from unittest.mock import patch

from langchain_core.documents import Document
from rag.uploads import (
    answer_uploaded_question,
    collection_name_for,
    documents_from_upload,
)


class UploadedDocumentTests(unittest.TestCase):
    def test_text_upload_keeps_filename_and_text(self):
        documents = documents_from_upload("notes.txt", b"\xef\xbb\xbfUseful notes")

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content, "Useful notes")
        self.assertEqual(documents[0].metadata, {"source": "notes.txt"})

    def test_upload_filename_is_reduced_to_its_basename(self):
        documents = documents_from_upload(r"C:\private\notes.txt", b"Useful notes")

        self.assertEqual(documents[0].metadata["source"], "notes.txt")

    def test_empty_text_upload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not contain readable text"):
            documents_from_upload("empty.txt", b" \n")

    def test_non_utf8_text_upload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be a UTF-8 text file"):
            documents_from_upload("notes.txt", b"\xff")

    def test_unsupported_file_type_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be a PDF or TXT file"):
            documents_from_upload("notes.docx", b"content")

    def test_unreadable_pdf_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "is not a readable PDF"):
            documents_from_upload("notes.pdf", b"not a PDF")

    def test_workspace_id_maps_to_a_valid_isolated_collection_name(self):
        workspace_id = str(uuid4())

        self.assertEqual(collection_name_for(workspace_id), f"uploads_{UUID(workspace_id).hex}")

    def test_invalid_workspace_id_is_rejected(self):
        with self.assertRaises(ValueError):
            collection_name_for("not-a-uuid")

    @patch("rag.uploads.ChatOllama")
    @patch("rag.uploads._vector_store")
    def test_follow_up_uses_recent_question_for_retrieval(
        self,
        vector_store,
        chat_model,
    ):
        retriever = vector_store.return_value.as_retriever.return_value
        retriever.invoke.return_value = [
            Document(
                page_content="The deadline is June 1.",
                metadata={"source": "calendar.txt"},
            )
        ]
        chat_model.return_value.invoke.return_value = SimpleNamespace(
            content="The deadline is June 1."
        )

        answer, sources = answer_uploaded_question(
            str(uuid4()),
            "When is it?",
            [("user", "What is the application deadline?")],
        )

        self.assertEqual(retriever.invoke.call_args.args[0],
                         "What is the application deadline? When is it?")
        self.assertEqual(answer, "The deadline is June 1.")
        self.assertEqual(sources, ["calendar.txt"])


if __name__ == "__main__":
    unittest.main()
