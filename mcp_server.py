from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# A tool to read a document's content
@mcp.tool(
    name="read_doc",
    description="Reads the contents of a document and return its content.",
)
def read_document(
    doc_id: str = Field(..., description="The ID of the document to read")
) -> str:
    if doc_id not in docs:
        raise ValueError("Document not found.")
    return docs[doc_id]

# A tool to edit a document's content
@mcp.tool(
    name="edit_doc",
    description="Edits the contents of a document by replacing it with new content.",
)
def edit_document(
    doc_id: str = Field(..., description="The ID of the document to edit"),
    old_content: str = Field(..., description="The old content of the document. Must match existing content."),
    new_content: str = Field(..., description="The new content for the document"),
) -> str:
    if doc_id not in docs:
        raise ValueError("Document not found.")
    if docs[doc_id] != old_content:
        raise ValueError("Old content does not match existing content.") 
    docs[doc_id] = new_content
    return docs[doc_id]

# A resource to return all doc id's
@mcp.resource(
    "docs://documents", #URI
    mime_type="application/json"
)
def list_documents() -> list[str]:
    return list(docs.keys())

# A resource to return the contents of a particular doc (templated resource)
@mcp.resource(
    "docs://documents/{doc_id}", #URI
    mime_type="text/plain"
)
def fetch_document(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with ID {doc_id} not found.")
    return docs[doc_id]

# A prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="rewrite_doc_md",
    description="Rewrite the provided document content in markdown format."
)
def format_document_md(
    doc_id: str = Field(..., description="The ID of the document to be reformatted.")
) -> list[base.Message]:
    prompt = f"""Your goal is to rewrite the content of the document with ID,
    <document_id>
    {doc_id}
    </document_id>
    Add in headings, subheadings, bullet points, and other markdown formatting as appropriate.
    Use the 'edit_doc' tool to update the document content once reformatted.
    """
    
    return [base.UserMessage(content=prompt)]

# A prompt to summarize a doc
@mcp.prompt(
    name="summarize_doc",
    description="Summarize the provided document content."
)
def summarize_document(
    doc_id: str = Field(..., description="The ID of the document to be summarized.")
) -> list[base.Message]:
    prompt = f"""Your goal is to summarize the content of the document with ID,
    <document_id>
    {doc_id}
    </document_id>
    Provide a concise summary highlighting the key points.
    """
    
    return [base.UserMessage(content=prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
