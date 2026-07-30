# from Pdf_Retriver_vectordb import retrieve_pdf_context
# from Escalate_msg import send_escalation_email
# from jira_connection import retrieve_jira_context



# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage
# import os
# import json
# from dotenv import load_dotenv

# load_dotenv()

# # llm = ChatGroq(
# #     model="llama-3.3-70b-versatile",
# #     temperature=0
# # )
# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0
# )

# # structured_llm = llm.with_structured_output(SupportResponse)


# def get_combined_context(user_question):

#     # --------------------------------
#     # 1. Search FMG Documentation
#     # --------------------------------

#     pdf_results = retrieve_pdf_context(
#         user_question,
#         k=5
#     )

#     # --------------------------------
#     # 2. Search Previous Jira Tickets
#     # --------------------------------

#     jira_results = retrieve_jira_context(
#         user_question,
#         max_results=5
#     )

#     # --------------------------------
#     # 3. Format PDF context
#     # --------------------------------

#     pdf_context = ""

#     for i, result in enumerate(pdf_results, 1):

#         pdf_context += f"""
# DOCUMENT SOURCE {i}
# Source: {result['source']}
# Page: {result['page']}

# {result['content']}

# --------------------------------
# """

#     # --------------------------------
#     # 4. Format Jira context
#     # --------------------------------

#     jira_context = ""

#     for i, ticket in enumerate(jira_results, 1):

#         jira_context += f"""
# PREVIOUS TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     # --------------------------------
#     # 5. Return combined context
#     # --------------------------------

#     return pdf_context, jira_context





# def answer_customer_question(user_question):

#     # ==========================================
#     # 1. RETRIEVE PDF DOCUMENTATION
#     # ==========================================

#     pdf_results = retrieve_pdf_context(
#         user_question,
#         k=5
#     )


#     # ==========================================
#     # 2. RETRIEVE PREVIOUS JIRA TICKETS
#     # ==========================================

#     jira_results = retrieve_jira_context(
#         user_question,
#         max_results=5
#     )


#     # ==========================================
#     # 3. FORMAT PDF CONTEXT
#     # ==========================================

#     pdf_context = ""

#     for i, result in enumerate(pdf_results, 1):

#         pdf_context += f"""
# DOCUMENT SOURCE {i}

# Source: {result['source']}
# Page: {result['page']}

# Content:
# {result['content']}

# --------------------------------
# """


#     # ==========================================
#     # 4. FORMAT JIRA CONTEXT
#     # ==========================================

#     jira_context = ""

#     for i, ticket in enumerate(jira_results, 1):

#         jira_context += f"""
# PREVIOUS SUPPORT TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """


#     # ==========================================
#     # 5. ASK LLM TO ANSWER + DECIDE ESCALATION
#     # ==========================================

#     prompt = f"""
# You are an AI Customer Support Engineer for FMG
# (Friday Media Group).

# Your job is to answer customer questions using ONLY:

# 1. FMG official documentation
# 2. Previous FMG customer support tickets

# You must not invent information.

# ========================================
# CUSTOMER QUESTION
# ========================================

# {user_question}


# ========================================
# FMG DOCUMENTATION
# ========================================

# {pdf_context}


# ========================================
# PREVIOUS JIRA SUPPORT TICKETS
# ========================================

# {jira_context}


# ========================================
# YOUR TASK
# ========================================

# Determine whether the customer's question can be
# confidently answered using the provided FMG documentation
# and previous Jira tickets.

# IMPORTANT ESCALATION RULE:

# Set "escalate" to true if:

# 1. The answer cannot be found in the provided FMG documentation
#    or previous Jira tickets.

# OR

# 2. The customer is asking for confidential, private,
#    sensitive, or unauthorized company information.

# OR

# 3. There is not enough reliable information to provide
#    a confident answer.

# Set "escalate" to false if the question can be
# confidently answered using the provided sources.

# ========================================
# OUTPUT FORMAT
# ========================================

# Return ONLY valid JSON.

# Use exactly this structure:

# {{
#     "answer": "Your answer to the customer",
#     "escalate": true,
#     "reason": "Why escalation is or is not required",
#     "sources": [
#         "FMG Documentation",
#         "Previous Support Ticket"
#     ]
# }}

# If escalation is required, the answer field should contain:

# "I am unable to provide a confident answer to your question
# based on the available FMG support information."

# If escalation is not required, provide a clear,
# professional answer based only on the available sources.

# The sources field should contain only the sources
# actually used to answer the question.
# """


#     # ==========================================
#     # 6. CALL GROQ LLM
#     # ==========================================

#     response = llm.invoke(
#         [HumanMessage(content=prompt)]
#     )


#     # ==========================================
#     # 7. PARSE LLM JSON RESPONSE
#     # ==========================================

#     try:

#         result = json.loads(response.content)

#     except json.JSONDecodeError:

#         print("⚠️ LLM did not return valid JSON.")

#         return (
#             "I am sorry, but I was unable to process your "
#             "request at this time."
#         )


#     # ==========================================
#     # 8. CHECK ESCALATION DECISION
#     # ==========================================

#     if result.get("escalate") is True:

#         print("\n⚠️ Escalation required.")

#         reason = result.get(
#             "reason",
#             "The AI could not confidently answer the question."
#         )


#         # ==========================================
#         # 9. SEND EMAIL TO ADMIN
#         # ==========================================

#         email_sent = send_escalation_email(
#             customer_question=user_question,
#             reason=reason
#         )


#         # ==========================================
#         # 10. RETURN CUSTOMER RESPONSE
#         # ==========================================

#         if email_sent:

#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# I have forwarded your query to FMG Support for further
# assistance. Our support team will review your request
# and provide further assistance.
# """

#         else:

#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# Your issue requires further investigation by FMG Support.
# """


#     # ==========================================
#     # 11. IF NO ESCALATION, RETURN LLM ANSWER
#     # ==========================================

#     return result.get(
#         "answer",
#         "I was unable to generate an answer."
#     )


# # ==========================================
# # RUN PROGRAM
# # ==========================================

# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("🤖 FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)

# def answer_customer_question(user_question):

#     pdf_context, jira_context = get_combined_context(
#         user_question
#     )

#     prompt = f"""
# You are an AI Customer Support Engineer for FMG
# (Friday Media Group).

# Your job is to answer the customer's question using
# the FMG documentation and previous customer support tickets.

# CUSTOMER QUESTION:
# {user_question}


# =============================
# FMG DOCUMENTATION
# =============================

# {pdf_context}


# =============================
# PREVIOUS SUPPORT TICKETS
# =============================

# {jira_context}


# =============================
# INSTRUCTIONS
# =============================

# 1. Answer the customer's question clearly and professionally.

# 2. Use the FMG documentation as the primary source
#    for official policies, instructions, and product information.

# 3. Use previous Jira tickets as supporting evidence
#    for similar customer problems and how they were resolved.

# 4. Do not invent information that is not supported
#    by the documentation or previous tickets.

# 5. If the documentation and tickets do not contain
#    enough information, clearly say that the issue
#    requires further investigation or escalation.

# 6. Explain why you selected the answer when appropriate.

# 7. Mention the source of your answer:
#    - FMG Documentation
#    - Previous Support Ticket
#    - Both

# 8. If the customer's issue cannot be confidently resolved,
#    recommend escalation to FMG Support.

# CUSTOMER RESPONSE:
# """

#     response = llm.invoke(
#         [HumanMessage(content=prompt)]
#     )

#     return response.content


# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("🤖 FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)







# from Pdf_Retriver_vectordb import retrieve_pdf_context
# from Escalate_msg import send_escalation_email
# from jira_connection import retrieve_jira_context

# import os
# import re
# import json
# from typing import List

# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage

# load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0
# )


# # ==========================================
# # STRUCTURED OUTPUT SCHEMA
# # ==========================================
# # Instead of asking the model to write JSON as free text (which it may wrap
# # in ```json fences, prepend a sentence to, or otherwise slightly malform --
# # that's what was causing "LLM did not return valid JSON" even when the
# # model's actual reasoning was fine), we bind this schema directly. Groq's
# # tool-calling support lets LangChain force the model to return a structured
# # object matching this shape, so there's no free-text JSON to parse or break.

# class SupportResponse(BaseModel):
#     answer: str = Field(description="The answer to give the customer")
#     escalate: bool = Field(description="True if this needs human escalation")
#     reason: str = Field(description="Why escalation is or is not required")
#     sources: List[str] = Field(
#         default_factory=list,
#         description="Which sources were actually used, e.g. 'FMG Documentation', 'Previous Support Ticket'",
#     )


# structured_llm = llm.with_structured_output(SupportResponse)


# def _extract_json_fallback(raw_text: str) -> dict:
#     """Defensive fallback for plain-text JSON: strips ```json fences and
#     pulls out the first {...} block, in case structured_llm isn't available
#     for some reason and you fall back to a raw llm.invoke() call."""
#     text = raw_text.strip()
#     text = re.sub(r"^```(?:json)?", "", text.strip())
#     text = re.sub(r"```$", "", text.strip())
#     text = text.strip()

#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     if match:
#         text = match.group(0)

#     return json.loads(text)


# def get_combined_context(user_question):
#     """Note: not currently called by answer_customer_question, which does
#     its own retrieval + formatting inline below. Kept in case other code
#     depends on it -- if nothing imports this, it can be deleted."""

#     pdf_results = retrieve_pdf_context(user_question, k=5)
#     jira_results = retrieve_jira_context(user_question, max_results=5)

#     pdf_context = ""
#     for i, result in enumerate(pdf_results, 1):
#         pdf_context += f"""
# DOCUMENT SOURCE {i}
# Source: {result['source']}
# Page: {result['page']}

# {result['content']}

# --------------------------------
# """

#     jira_context = ""
#     for i, ticket in enumerate(jira_results, 1):
#         jira_context += f"""
# PREVIOUS TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     return pdf_context, jira_context


# def answer_customer_question(user_question):

#     # ==========================================
#     # 1. RETRIEVE PDF DOCUMENTATION
#     # ==========================================

#     pdf_results = retrieve_pdf_context(
#         user_question,
#         k=5
#     )

#     # ==========================================
#     # 2. RETRIEVE PREVIOUS JIRA TICKETS
#     # ==========================================

#     jira_results = retrieve_jira_context(
#         user_question,
#         max_results=5
#     )

#     # ==========================================
#     # 3. FORMAT PDF CONTEXT
#     # ==========================================

#     pdf_context = ""

#     for i, result in enumerate(pdf_results, 1):

#         pdf_context += f"""
# DOCUMENT SOURCE {i}

# Source: {result['source']}
# Page: {result['page']}

# Content:
# {result['content']}

# --------------------------------
# """

#     # ==========================================
#     # 4. FORMAT JIRA CONTEXT
#     # ==========================================

#     jira_context = ""

#     for i, ticket in enumerate(jira_results, 1):

#         jira_context += f"""
# PREVIOUS SUPPORT TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     # ==========================================
#     # 5. BUILD PROMPT (no longer needs to beg for raw JSON --
#     #    the schema is enforced by with_structured_output below)
#     # ==========================================

#     prompt = f"""
# You are an AI Customer Support Engineer for FMG
# (Friday Media Group).

# Your job is to answer customer questions using ONLY:

# 1. FMG official documentation
# 2. Previous FMG customer support tickets

# You must not invent information.

# ========================================
# CUSTOMER QUESTION
# ========================================

# {user_question}


# ========================================
# FMG DOCUMENTATION
# ========================================

# {pdf_context}


# ========================================
# PREVIOUS JIRA SUPPORT TICKETS
# ========================================

# {jira_context}


# ========================================
# YOUR TASK
# ========================================

# Determine whether the customer's question can be
# confidently answered using the provided FMG documentation
# and previous Jira tickets.

# IMPORTANT ESCALATION RULE:

# Set "escalate" to true if:

# 1. The answer cannot be found in the provided FMG documentation
#    or previous Jira tickets.

# OR

# 2. The customer is asking for confidential, private,
#    sensitive, or unauthorized company information.

# OR

# 3. There is not enough reliable information to provide
#    a confident answer.

# Set "escalate" to false if the question can be
# confidently answered using the provided sources.

# If escalation is required, the "answer" field should contain:

# "I am unable to provide a confident answer to your question
# based on the available FMG support information."

# If escalation is not required, "answer" should be a clear,
# professional answer based only on the available sources.

# The "sources" field should contain only the sources
# actually used to answer the question.
# """

#     # ==========================================
#     # 6. CALL GROQ LLM WITH STRUCTURED OUTPUT
#     # ==========================================

#     try:
#         result = structured_llm.invoke([HumanMessage(content=prompt)])
#         # result is a SupportResponse pydantic object (not a dict)
#         escalate = result.escalate
#         answer_text = result.answer
#         reason = result.reason

#     except Exception as exc:
#         # Fallback path: something went wrong with structured output itself
#         # (e.g. transient API issue). Try a plain-text call + defensive
#         # parsing rather than failing outright.
#         print(f"Structured output failed ({exc}); falling back to raw JSON parsing.")
#         try:
#             raw_response = llm.invoke([HumanMessage(content=prompt + '\n\nReturn ONLY a JSON object with keys: answer, escalate, reason, sources.')])
#             parsed = _extract_json_fallback(raw_response.content)
#             escalate = bool(parsed.get("escalate", True))
#             answer_text = parsed.get("answer", "I was unable to generate an answer.")
#             reason = parsed.get("reason", "The AI could not confidently answer the question.")
#         except Exception as exc2:
#             print(f"Fallback parsing also failed ({exc2}).")
#             return (
#                 "I am sorry, but I was unable to process your "
#                 "request at this time."
#             )

#     # ==========================================
#     # 7. CHECK ESCALATION DECISION
#     # ==========================================

#     if escalate:

#         print("\nEscalation required.")

#         # ==========================================
#         # 8. SEND EMAIL TO ADMIN
#         # ==========================================

#         email_sent = send_escalation_email(
#             customer_question=user_question,
#             reason=reason
#         )

#         # ==========================================
#         # 9. RETURN CUSTOMER RESPONSE
#         # ==========================================

#         if email_sent:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# I have forwarded your query to FMG Support for further
# assistance. Our support team will review your request
# and provide further assistance.
# """
#         else:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# Your issue requires further investigation by FMG Support.
# """

#     # ==========================================
#     # 10. IF NO ESCALATION, RETURN LLM ANSWER
#     # ==========================================

#     return answer_text


# # ==========================================
# # RUN PROGRAM
# # ==========================================

# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)





# from Pdf_Retriver_vectordb import retrieve_pdf_context
# from Escalate_msg import send_escalation_email
# from jira_connection import retrieve_jira_context

# import os
# import re
# import json
# from typing import List, Literal

# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage

# load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0
# )


# # ==========================================
# # STRUCTURED OUTPUT SCHEMA
# # ==========================================
# # Same idea as before (tool-calling schema instead of free-text JSON, so
# # nothing can be malformed) - but "sources" is no longer just a generic
# # label. It's now a list of Citation objects that force the model to name
# # the *specific* document/page or ticket it actually used, so those
# # citations can be shown to the customer, not just silently captured.

# class Citation(BaseModel):
#     source_type: Literal["FMG Documentation", "Previous Support Ticket"] = Field(
#         description="Which kind of source this citation comes from"
#     )
#     reference: str = Field(
#         description=(
#             "The SPECIFIC identifier for this source, taken directly from the "
#             "context provided. For FMG Documentation this must be the document "
#             "name and page number, e.g. 'user-guide.pdf, page 12'. For a "
#             "Previous Support Ticket this must be the ticket key, e.g. 'SUP-482'. "
#             "Never leave this generic - always copy the exact source/page or "
#             "ticket ID shown in the provided context."
#         )
#     )


# class SupportResponse(BaseModel):
#     answer: str = Field(description="The answer to give the customer")
#     escalate: bool = Field(description="True if this needs human escalation")
#     reason: str = Field(description="Why escalation is or is not required")
#     sources: List[Citation] = Field(
#         default_factory=list,
#         description=(
#             "Every specific document page or ticket actually used to build the "
#             "answer. Empty if escalate is true or if no source was used."
#         ),
#     )


# structured_llm = llm.with_structured_output(SupportResponse)


# def _extract_json_fallback(raw_text: str) -> dict:
#     """Defensive fallback for plain-text JSON: strips ```json fences and
#     pulls out the first {...} block, in case structured_llm isn't available
#     for some reason and you fall back to a raw llm.invoke() call."""
#     text = raw_text.strip()
#     text = re.sub(r"^```(?:json)?", "", text.strip())
#     text = re.sub(r"```$", "", text.strip())
#     text = text.strip()

#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     if match:
#         text = match.group(0)

#     return json.loads(text)


# def _format_citations(sources) -> str:
#     """Turns the structured citation list into a readable 'Sources:' block.
#     Accepts either Citation pydantic objects or plain dicts (the fallback
#     JSON path returns dicts, the structured path returns Citation objects).
#     """
#     if not sources:
#         return ""

#     lines = []
#     for src in sources:
#         if isinstance(src, dict):
#             source_type = src.get("source_type", "Source")
#             reference = src.get("reference", "").strip()
#         else:
#             source_type = src.source_type
#             reference = src.reference.strip()

#         if not reference:
#             continue
#         lines.append(f"- {source_type}: {reference}")

#     if not lines:
#         return ""

#     return "\n\nSources:\n" + "\n".join(lines)


# def get_combined_context(user_question):
#     """Note: not currently called by answer_customer_question, which does
#     its own retrieval + formatting inline below. Kept in case other code
#     depends on it -- if nothing imports this, it can be deleted."""

#     pdf_results = retrieve_pdf_context(user_question, k=5)
#     jira_results = retrieve_jira_context(user_question, max_results=5)

#     pdf_context = ""
#     for i, result in enumerate(pdf_results, 1):
#         pdf_context += f"""
# DOCUMENT SOURCE {i}
# Source: {result['source']}
# Page: {result['page']}

# {result['content']}

# --------------------------------
# """

#     jira_context = ""
#     for i, ticket in enumerate(jira_results, 1):
#         jira_context += f"""
# PREVIOUS TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     return pdf_context, jira_context


# def answer_customer_question(user_question):

#     # ==========================================
#     # 1. RETRIEVE PDF DOCUMENTATION
#     # ==========================================

#     pdf_results = retrieve_pdf_context(
#         user_question,
#         k=5
#     )

#     # ==========================================
#     # 2. RETRIEVE PREVIOUS JIRA TICKETS
#     # ==========================================

#     jira_results = retrieve_jira_context(
#         user_question,
#         max_results=5
#     )

#     # ==========================================
#     # 3. FORMAT PDF CONTEXT
#     # ==========================================

#     pdf_context = ""

#     for i, result in enumerate(pdf_results, 1):

#         pdf_context += f"""
# DOCUMENT SOURCE {i}

# Source: {result['source']}
# Page: {result['page']}

# Content:
# {result['content']}

# --------------------------------
# """

#     # ==========================================
#     # 4. FORMAT JIRA CONTEXT
#     # ==========================================

#     jira_context = ""

#     for i, ticket in enumerate(jira_results, 1):

#         jira_context += f"""
# PREVIOUS SUPPORT TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     # ==========================================
#     # 5. BUILD PROMPT
#     # ==========================================
#     # The schema is enforced by with_structured_output below, but the model
#     # still has to be told WHERE to find the identifiers it must put in
#     # each citation's "reference" field - hence pointing it at the exact
#     # "Source:"/"Page:"/"Ticket ID:" labels already present in the context.

#     prompt = f"""
# You are an AI Customer Support Engineer for FMG
# (Friday Media Group).

# Your job is to answer customer questions using ONLY:

# 1. FMG official documentation
# 2. Previous FMG customer support tickets

# You must not invent information.

# ========================================
# CUSTOMER QUESTION
# ========================================

# {user_question}


# ========================================
# FMG DOCUMENTATION
# ========================================

# {pdf_context}


# ========================================
# PREVIOUS JIRA SUPPORT TICKETS
# ========================================

# {jira_context}


# ========================================
# YOUR TASK
# ========================================

# Determine whether the customer's question can be
# confidently answered using the provided FMG documentation
# and previous Jira tickets.

# IMPORTANT ESCALATION RULE:

# Set "escalate" to true if:

# 1. The answer cannot be found in the provided FMG documentation
#    or previous Jira tickets.

# OR

# 2. The customer is asking for confidential, private,
#    sensitive, or unauthorized company information.

# OR

# 3. There is not enough reliable information to provide
#    a confident answer.

# Set "escalate" to false if the question can be
# confidently answered using the provided sources.

# If escalation is required, the "answer" field should contain:

# "I am unable to provide a confident answer to your question
# based on the available FMG support information."
# Leave "sources" empty in this case.

# If escalation is not required, "answer" should be a clear,
# professional answer based only on the available sources.

# ========================================
# CITATION RULES (IMPORTANT)
# ========================================

# For every piece of information you actually used in the answer,
# add one entry to "sources" with:

# - source_type: "FMG Documentation" or "Previous Support Ticket"
# - reference: the EXACT identifier shown in the context above -
#   for documentation, copy the "Source:" filename together with the
#   "Page:" number exactly as written (e.g. "user-guide.pdf, page 12");
#   for a ticket, copy the exact "Ticket ID:" value (e.g. "SUP-482").

# Do not invent a reference. Do not use a vague label like just
# "FMG Documentation" with no page, or "Previous Support Ticket" with
# no ticket ID - always include the specific identifier from the
# context. Only cite sources you actually relied on; do not cite a
# document or ticket that was provided but not used.
# """

#     # ==========================================
#     # 6. CALL GROQ LLM WITH STRUCTURED OUTPUT
#     # ==========================================

#     try:
#         result = structured_llm.invoke([HumanMessage(content=prompt)])
#         # result is a SupportResponse pydantic object (not a dict)
#         escalate = result.escalate
#         answer_text = result.answer
#         reason = result.reason
#         sources = result.sources  # list[Citation]

#     except Exception as exc:
#         # Fallback path: something went wrong with structured output itself
#         # (e.g. transient API issue). Try a plain-text call + defensive
#         # parsing rather than failing outright.
#         print(f"Structured output failed ({exc}); falling back to raw JSON parsing.")
#         try:
#             fallback_prompt = prompt + (
#                 "\n\nReturn ONLY a JSON object with keys: answer, escalate, "
#                 "reason, sources. 'sources' must be a list of objects like "
#                 '{"source_type": "...", "reference": "..."}.'
#             )
#             raw_response = llm.invoke([HumanMessage(content=fallback_prompt)])
#             parsed = _extract_json_fallback(raw_response.content)
#             escalate = bool(parsed.get("escalate", True))
#             answer_text = parsed.get("answer", "I was unable to generate an answer.")
#             reason = parsed.get("reason", "The AI could not confidently answer the question.")
#             sources = parsed.get("sources", [])  # list[dict]
#         except Exception as exc2:
#             print(f"Fallback parsing also failed ({exc2}).")
#             return (
#                 "I am sorry, but I was unable to process your "
#                 "request at this time."
#             )

#     # ==========================================
#     # 7. CHECK ESCALATION DECISION
#     # ==========================================

#     if escalate:

#         print("\nEscalation required.")

#         # ==========================================
#         # 8. SEND EMAIL TO ADMIN
#         # ==========================================

#         email_sent = send_escalation_email(
#             customer_question=user_question,
#             reason=reason
#         )

#         # ==========================================
#         # 9. RETURN CUSTOMER RESPONSE
#         # ==========================================

#         if email_sent:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# I have forwarded your query to FMG Support for further
# assistance. Our support team will review your request
# and provide further assistance.
# """
#         else:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# Your issue requires further investigation by FMG Support.
# """

#     # ==========================================
#     # 10. IF NO ESCALATION, RETURN LLM ANSWER + CITED SOURCES
#     # ==========================================

#     return answer_text + _format_citations(sources)


# # ==========================================
# # RUN PROGRAM
# # ==========================================

# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)



# from Pdf_Retriver_vectordb import retrieve_pdf_context
# from Escalate_msg import send_escalation_email
# from jira_connection import retrieve_jira_context

# import os
# import re
# import json
# from typing import List, Literal

# from dotenv import load_dotenv
# from pydantic import BaseModel, Field
# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage

# load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     temperature=0
# )


# # ==========================================
# # STRUCTURED OUTPUT SCHEMA
# # ==========================================
# # Same idea as before (tool-calling schema instead of free-text JSON, so
# # nothing can be malformed) - but "sources" is no longer just a generic
# # label. It's now a list of Citation objects that force the model to name
# # the *specific* document/page or ticket it actually used, so those
# # citations can be shown to the customer, not just silently captured.

# class Citation(BaseModel):
#     source_type: Literal["FMG Documentation", "Previous Support Ticket"] = Field(
#         description="Which kind of source this citation comes from"
#     )
#     reference: str = Field(
#         description=(
#             "The SPECIFIC identifier for this source, taken directly from the "
#             "context provided. For FMG Documentation this must be the document "
#             "name and page number, e.g. 'user-guide.pdf, page 12'. For a "
#             "Previous Support Ticket this must be the ticket key, e.g. 'SUP-482'. "
#             "Never leave this generic - always copy the exact source/page or "
#             "ticket ID shown in the provided context."
#         )
#     )


# class SupportResponse(BaseModel):
#     answer: str = Field(description="The answer to give the customer")
#     escalate: bool = Field(description="True if this needs human escalation")
#     reason: str = Field(description="Why escalation is or is not required")
#     sources: List[Citation] = Field(
#         default_factory=list,
#         description=(
#             "Every specific document page or ticket actually used to build the "
#             "answer. Empty if escalate is true or if no source was used."
#         ),
#     )


# structured_llm = llm.with_structured_output(SupportResponse)


# def _extract_json_fallback(raw_text: str) -> dict:
#     """Defensive fallback for plain-text JSON: strips ```json fences and
#     pulls out the first {...} block, in case structured_llm isn't available
#     for some reason and you fall back to a raw llm.invoke() call."""
#     text = raw_text.strip()
#     text = re.sub(r"^```(?:json)?", "", text.strip())
#     text = re.sub(r"```$", "", text.strip())
#     text = text.strip()

#     match = re.search(r"\{.*\}", text, re.DOTALL)
#     if match:
#         text = match.group(0)

#     return json.loads(text)


# def _format_citations(sources) -> str:
#     """Turns the structured citation list into a readable 'Sources:' block.
#     Accepts either Citation pydantic objects or plain dicts (the fallback
#     JSON path returns dicts, the structured path returns Citation objects).
#     """
#     if not sources:
#         return ""

#     lines = []
#     for src in sources:
#         if isinstance(src, dict):
#             source_type = src.get("source_type", "Source")
#             reference = src.get("reference", "").strip()
#         else:
#             source_type = src.source_type
#             reference = src.reference.strip()

#         if not reference:
#             continue
#         lines.append(f"- {source_type}: {reference}")

#     if not lines:
#         return ""

#     return "\n\nSources:\n" + "\n".join(lines)


# def get_combined_context(user_question):
#     """Note: not currently called by answer_customer_question, which does
#     its own retrieval + formatting inline below. Kept in case other code
#     depends on it -- if nothing imports this, it can be deleted."""

#     pdf_results = retrieve_pdf_context(user_question, k=5)
#     jira_results = retrieve_jira_context(user_question, max_results=5)

#     pdf_context = ""
#     for i, result in enumerate(pdf_results, 1):
#         pdf_context += f"""
# DOCUMENT SOURCE {i}
# Source: {result['source']}
# Page: {result['page']}

# {result['content']}

# --------------------------------
# """

#     jira_context = ""
#     for i, ticket in enumerate(jira_results, 1):
#         jira_context += f"""
# PREVIOUS TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     return pdf_context, jira_context


# def answer_customer_question(user_question):

#     # ==========================================
#     # 1. RETRIEVE PDF DOCUMENTATION
#     # ==========================================

#     pdf_results = retrieve_pdf_context(
#         user_question,
#         k=5
#     )

#     # ==========================================
#     # 2. RETRIEVE PREVIOUS JIRA TICKETS
#     # ==========================================

#     jira_results = retrieve_jira_context(
#         user_question,
#         max_results=5
#     )

#     # DEBUG: if the answer only ever cites tickets and never PDFs, check
#     # this line first. If pdf_results is empty (or 0 results) for a
#     # question you know the docs cover, the problem is in
#     # retrieve_pdf_context / the vector store, not in the LLM prompt -
#     # the model can't cite content it was never given.
#     print(f"[debug] retrieved {len(pdf_results)} PDF chunk(s), "
#           f"{len(jira_results)} Jira ticket(s) for this question")

#     # ==========================================
#     # 3. FORMAT PDF CONTEXT
#     # ==========================================

#     pdf_context = ""

#     for i, result in enumerate(pdf_results, 1):

#         pdf_context += f"""
# DOCUMENT SOURCE {i}

# Source: {result['source']}
# Page: {result['page']}

# Content:
# {result['content']}

# --------------------------------
# """

#     # ==========================================
#     # 4. FORMAT JIRA CONTEXT
#     # ==========================================

#     jira_context = ""

#     for i, ticket in enumerate(jira_results, 1):

#         jira_context += f"""
# PREVIOUS SUPPORT TICKET {i}

# Ticket ID:
# {ticket['ticket_key']}

# Summary:
# {ticket['summary']}

# Description:
# {ticket['description']}

# --------------------------------
# """

#     # ==========================================
#     # 5. BUILD PROMPT
#     # ==========================================
#     # The schema is enforced by with_structured_output below, but the model
#     # still has to be told WHERE to find the identifiers it must put in
#     # each citation's "reference" field - hence pointing it at the exact
#     # "Source:"/"Page:"/"Ticket ID:" labels already present in the context.

#     prompt = f"""
# You are an AI Customer Support Engineer for FMG
# (Friday Media Group).

# Your job is to answer customer questions using ONLY:

# 1. FMG official documentation
# 2. Previous FMG customer support tickets

# You must not invent information.

# ========================================
# CUSTOMER QUESTION
# ========================================

# {user_question}


# ========================================
# FMG DOCUMENTATION
# ========================================

# {pdf_context}


# ========================================
# PREVIOUS JIRA SUPPORT TICKETS
# ========================================

# {jira_context}


# ========================================
# YOUR TASK
# ========================================

# Determine whether the customer's question can be
# confidently answered using the provided FMG documentation
# and previous Jira tickets.

# IMPORTANT - USE BOTH SOURCE TYPES:

# The FMG DOCUMENTATION and PREVIOUS JIRA SUPPORT TICKETS sections
# above are two SEPARATE sources of evidence. Before writing your
# answer:

# 1. Read through EVERY document source listed above and note which
#    ones (if any) are relevant to the customer's question.
# 2. Read through EVERY previous ticket listed above and note which
#    ones (if any) are relevant to the customer's question.
# 3. If BOTH documentation and ticket(s) contain information relevant
#    to the question, your answer MUST be built from both, and your
#    "sources" list MUST include at least one citation from each type.
# 4. Do not answer using only one source type if the other section
#    also contains relevant information - a ticket confirming or
#    illustrating something is not a substitute for citing the
#    documentation that actually defines it, and vice versa.
# 5. Only omit a source type entirely if it truly contains nothing
#    relevant to this specific question.

# IMPORTANT ESCALATION RULE:

# Set "escalate" to true if:

# 1. The answer cannot be found in the provided FMG documentation
#    or previous Jira tickets.

# OR

# 2. The customer is asking for confidential, private,
#    sensitive, or unauthorized company information.

# OR

# 3. There is not enough reliable information to provide
#    a confident answer.

# Set "escalate" to false if the question can be
# confidently answered using the provided sources.

# If escalation is required, the "answer" field should contain:

# "I am unable to provide a confident answer to your question
# based on the available FMG support information."
# Leave "sources" empty in this case.

# If escalation is not required, "answer" should be a clear,
# professional answer based only on the available sources.

# ========================================
# CITATION RULES (IMPORTANT)
# ========================================

# For every piece of information you actually used in the answer,
# add one entry to "sources" with:

# - source_type: "FMG Documentation" or "Previous Support Ticket"
# - reference: the EXACT identifier shown in the context above -
#   for documentation, copy the "Source:" filename together with the
#   "Page:" number exactly as written (e.g. "user-guide.pdf, page 12");
#   for a ticket, copy the exact "Ticket ID:" value (e.g. "SUP-482").

# Do not invent a reference. Do not use a vague label like just
# "FMG Documentation" with no page, or "Previous Support Ticket" with
# no ticket ID - always include the specific identifier from the
# context. Only cite sources you actually relied on; do not cite a
# document or ticket that was provided but not used.
# """

#     # ==========================================
#     # 6. CALL GROQ LLM WITH STRUCTURED OUTPUT
#     # ==========================================

#     try:
#         result = structured_llm.invoke([HumanMessage(content=prompt)])
#         # result is a SupportResponse pydantic object (not a dict)
#         escalate = result.escalate
#         answer_text = result.answer
#         reason = result.reason
#         sources = result.sources  # list[Citation]

#     except Exception as exc:
#         # Fallback path: something went wrong with structured output itself
#         # (e.g. transient API issue). Try a plain-text call + defensive
#         # parsing rather than failing outright.
#         print(f"Structured output failed ({exc}); falling back to raw JSON parsing.")
#         try:
#             fallback_prompt = prompt + (
#                 "\n\nReturn ONLY a JSON object with keys: answer, escalate, "
#                 "reason, sources. 'sources' must be a list of objects like "
#                 '{"source_type": "...", "reference": "..."}.'
#             )
#             raw_response = llm.invoke([HumanMessage(content=fallback_prompt)])
#             parsed = _extract_json_fallback(raw_response.content)
#             escalate = bool(parsed.get("escalate", True))
#             answer_text = parsed.get("answer", "I was unable to generate an answer.")
#             reason = parsed.get("reason", "The AI could not confidently answer the question.")
#             sources = parsed.get("sources", [])  # list[dict]
#         except Exception as exc2:
#             print(f"Fallback parsing also failed ({exc2}).")
#             return (
#                 "I am sorry, but I was unable to process your "
#                 "request at this time."
#             )

#     # ==========================================
#     # 7. CHECK ESCALATION DECISION
#     # ==========================================

#     if escalate:

#         print("\nEscalation required.")

#         # ==========================================
#         # 8. SEND EMAIL TO ADMIN
#         # ==========================================

#         email_sent = send_escalation_email(
#             customer_question=user_question,
#             reason=reason
#         )

#         # ==========================================
#         # 9. RETURN CUSTOMER RESPONSE
#         # ==========================================

#         if email_sent:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# I have forwarded your query to FMG Support for further
# assistance. Our support team will review your request
# and provide further assistance.
# """
#         else:
#             return """
# I am unable to provide a confident answer to your question
# based on the available FMG support information.

# Your issue requires further investigation by FMG Support.
# """

#     # ==========================================
#     # 10. IF NO ESCALATION, RETURN LLM ANSWER + CITED SOURCES
#     # ==========================================

#     return answer_text + _format_citations(sources)


# # ==========================================
# # RUN PROGRAM
# # ==========================================

# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)



from Pdf_Retriver_vectordb import retrieve_pdf_context
from Escalate_msg import send_escalation_email
from jira_connection import retrieve_jira_context
from frontend import run_frontend

import os
import re
import json
from typing import List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


# ==========================================
# STRUCTURED OUTPUT SCHEMA
# ==========================================
# Same idea as before (tool-calling schema instead of free-text JSON, so
# nothing can be malformed) - but "sources" is no longer just a generic
# label. It's now a list of Citation objects that force the model to name
# the *specific* document/page or ticket it actually used, so those
# citations can be shown to the customer, not just silently captured.

class Citation(BaseModel):
    source_type: Literal["FMG Documentation", "Previous Support Ticket"] = Field(
        description="Which kind of source this citation comes from"
    )
    reference: str = Field(
        description=(
            "The SPECIFIC identifier for this source, taken directly from the "
            "context provided. For FMG Documentation this must be the document "
            "name and page number, e.g. 'user-guide.pdf, page 12'. For a "
            "Previous Support Ticket this must be the ticket key, e.g. 'SUP-482'. "
            "Never leave this generic - always copy the exact source/page or "
            "ticket ID shown in the provided context."
        )
    )


class SupportResponse(BaseModel):
    answer: str = Field(description="The answer to give the customer")
    escalate: bool = Field(description="True if this needs human escalation")
    reason: str = Field(description="Why escalation is or is not required")
    sources: List[Citation] = Field(
        default_factory=list,
        description=(
            "Every specific document page or ticket actually used to build the "
            "answer. Empty if escalate is true or if no source was used."
        ),
    )
    draft_ticket_reply: str = Field(
        description=(
            "A ready-to-post draft reply for the support ticket/thread, written "
            "as if a support agent is sending it to the customer. Professional "
            "and friendly tone, opens with a greeting, resolves or acknowledges "
            "the question, and closes with a sign-off. If escalate is true, this "
            "should acknowledge the question and let the customer know it has "
            "been forwarded to the FMG support team for further review, rather "
            "than attempting to answer it."
        )
    )


structured_llm = llm.with_structured_output(SupportResponse)


def _extract_json_fallback(raw_text: str) -> dict:
    """Defensive fallback for plain-text JSON: strips ```json fences and
    pulls out the first {...} block, in case structured_llm isn't available
    for some reason and you fall back to a raw llm.invoke() call."""
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?", "", text.strip())
    text = re.sub(r"```$", "", text.strip())
    text = text.strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


def _format_citations(sources) -> str:
    """Turns the structured citation list into a readable 'Sources:' block.
    Accepts either Citation pydantic objects or plain dicts (the fallback
    JSON path returns dicts, the structured path returns Citation objects).
    """
    if not sources:
        return ""

    lines = []
    for src in sources:
        if isinstance(src, dict):
            source_type = src.get("source_type", "Source")
            reference = src.get("reference", "").strip()
        else:
            source_type = src.source_type
            reference = src.reference.strip()

        if not reference:
            continue
        lines.append(f"- {source_type}: {reference}")

    if not lines:
        return ""

    return "\n\nSources:\n" + "\n".join(lines)


def _format_draft_reply(draft_reply: str) -> str:
    """Formats the draft ticket reply as its own labeled section, so it's
    clearly separated from the customer-facing answer and the sources
    list rather than blended into the same paragraph."""
    draft_reply = (draft_reply or "").strip()
    if not draft_reply:
        return ""
    return "\n\nDraft Ticket Reply:\n" + draft_reply


def get_combined_context(user_question):
    """Note: not currently called by answer_customer_question, which does
    its own retrieval + formatting inline below. Kept in case other code
    depends on it -- if nothing imports this, it can be deleted."""

    pdf_results = retrieve_pdf_context(user_question, k=5)
    jira_results = retrieve_jira_context(user_question, max_results=5)

    pdf_context = ""
    for i, result in enumerate(pdf_results, 1):
        pdf_context += f"""
DOCUMENT SOURCE {i}
Source: {result['source']}
Page: {result['page']}

{result['content']}

--------------------------------
"""

    jira_context = ""
    for i, ticket in enumerate(jira_results, 1):
        jira_context += f"""
PREVIOUS TICKET {i}

Ticket ID:
{ticket['ticket_key']}

Summary:
{ticket['summary']}

Description:
{ticket['description']}

--------------------------------
"""

    return pdf_context, jira_context


def answer_customer_question(user_question):

    # ==========================================
    # 1. RETRIEVE PDF DOCUMENTATION
    # ==========================================

    pdf_results = retrieve_pdf_context(
        user_question,
        k=5
    )

    # ==========================================
    # 2. RETRIEVE PREVIOUS JIRA TICKETS
    # ==========================================

    jira_results = retrieve_jira_context(
        user_question,
        max_results=5
    )

    # DEBUG: if the answer only ever cites tickets and never PDFs, check
    # this line first. If pdf_results is empty (or 0 results) for a
    # question you know the docs cover, the problem is in
    # retrieve_pdf_context / the vector store, not in the LLM prompt -
    # the model can't cite content it was never given.
    print(f"[debug] retrieved {len(pdf_results)} PDF chunk(s), "
          f"{len(jira_results)} Jira ticket(s) for this question")

    # ==========================================
    # 3. FORMAT PDF CONTEXT
    # ==========================================

    pdf_context = ""

    for i, result in enumerate(pdf_results, 1):

        pdf_context += f"""
DOCUMENT SOURCE {i}

Source: {result['source']}
Page: {result['page']}

Content:
{result['content']}

--------------------------------
"""

    # ==========================================
    # 4. FORMAT JIRA CONTEXT
    # ==========================================

    jira_context = ""

    for i, ticket in enumerate(jira_results, 1):

        jira_context += f"""
PREVIOUS SUPPORT TICKET {i}

Ticket ID:
{ticket['ticket_key']}

Summary:
{ticket['summary']}

Description:
{ticket['description']}

--------------------------------
"""

    # ==========================================
    # 5. BUILD PROMPT
    # ==========================================
    # The schema is enforced by with_structured_output below, but the model
    # still has to be told WHERE to find the identifiers it must put in
    # each citation's "reference" field - hence pointing it at the exact
    # "Source:"/"Page:"/"Ticket ID:" labels already present in the context.

    prompt = f"""
You are an AI Customer Support Engineer for FMG
(Friday Media Group).

Your job is to answer customer questions using ONLY:

1. FMG official documentation
2. Previous FMG customer support tickets

You must not invent information.

========================================
CUSTOMER QUESTION
========================================

{user_question}


========================================
FMG DOCUMENTATION
========================================

{pdf_context}


========================================
PREVIOUS JIRA SUPPORT TICKETS
========================================

{jira_context}


========================================
YOUR TASK
========================================

Determine whether the customer's question can be
confidently answered using the provided FMG documentation
and previous Jira tickets.

IMPORTANT - USE BOTH SOURCE TYPES:

The FMG DOCUMENTATION and PREVIOUS JIRA SUPPORT TICKETS sections
above are two SEPARATE sources of evidence. Before writing your
answer:

1. Read through EVERY document source listed above and note which
   ones (if any) are relevant to the customer's question.
2. Read through EVERY previous ticket listed above and note which
   ones (if any) are relevant to the customer's question.
3. If BOTH documentation and ticket(s) contain information relevant
   to the question, your answer MUST be built from both, and your
   "sources" list MUST include at least one citation from each type.
4. Do not answer using only one source type if the other section
   also contains relevant information - a ticket confirming or
   illustrating something is not a substitute for citing the
   documentation that actually defines it, and vice versa.
5. Only omit a source type entirely if it truly contains nothing
   relevant to this specific question.

IMPORTANT ESCALATION RULE:

Set "escalate" to true if:

1. The answer cannot be found in the provided FMG documentation
   or previous Jira tickets.

OR

2. The customer is asking for confidential, private,
   sensitive, or unauthorized company information.

OR

3. There is not enough reliable information to provide
   a confident answer.

Set "escalate" to false if the question can be
confidently answered using the provided sources.

If escalation is required, the "answer" field should contain:

"I am unable to provide a confident answer to your question
based on the available FMG support information."
Leave "sources" empty in this case.

If escalation is not required, "answer" should be a clear,
professional answer based only on the available sources.

========================================
CITATION RULES (IMPORTANT)
========================================

For every piece of information you actually used in the answer,
add one entry to "sources" with:

- source_type: "FMG Documentation" or "Previous Support Ticket"
- reference: the EXACT identifier shown in the context above -
  for documentation, copy the "Source:" filename together with the
  "Page:" number exactly as written (e.g. "user-guide.pdf, page 12");
  for a ticket, copy the exact "Ticket ID:" value (e.g. "SUP-482").

Do not invent a reference. Do not use a vague label like just
"FMG Documentation" with no page, or "Previous Support Ticket" with
no ticket ID - always include the specific identifier from the
context. Only cite sources you actually relied on; do not cite a
document or ticket that was provided but not used.

========================================
DRAFT TICKET REPLY (IMPORTANT)
========================================

In addition to "answer", write a "draft_ticket_reply" - a ready-to-post
reply a support agent could paste directly into the ticket/thread with
little or no editing.

- Open with a brief greeting to the customer.
- If escalate is false: give the resolution clearly and helpfully,
  based only on the same sources used in "answer". You may naturally
  mention where the information comes from (e.g. "as covered in our
  user guide") without necessarily repeating the raw reference format
  used in "sources".
- If escalate is true: do NOT attempt to answer the question. Instead
  acknowledge it was received and let the customer know it has been
  forwarded to the FMG support team for further review.
- Close with a short, professional sign-off.
- Keep it self-contained - it should make sense on its own, without
  needing the "answer" or "sources" fields alongside it.
"""

    # ==========================================
    # 6. CALL GROQ LLM WITH STRUCTURED OUTPUT
    # ==========================================

    try:
        result = structured_llm.invoke([HumanMessage(content=prompt)])
        # result is a SupportResponse pydantic object (not a dict)
        escalate = result.escalate
        answer_text = result.answer
        reason = result.reason
        sources = result.sources  # list[Citation]
        draft_reply = result.draft_ticket_reply

    except Exception as exc:
        # Fallback path: something went wrong with structured output itself
        # (e.g. transient API issue). Try a plain-text call + defensive
        # parsing rather than failing outright.
        print(f"Structured output failed ({exc}); falling back to raw JSON parsing.")
        try:
            fallback_prompt = prompt + (
                "\n\nReturn ONLY a JSON object with keys: answer, escalate, "
                "reason, sources, draft_ticket_reply. 'sources' must be a list "
                'of objects like {"source_type": "...", "reference": "..."}.'
            )
            raw_response = llm.invoke([HumanMessage(content=fallback_prompt)])
            parsed = _extract_json_fallback(raw_response.content)
            escalate = bool(parsed.get("escalate", True))
            answer_text = parsed.get("answer", "I was unable to generate an answer.")
            reason = parsed.get("reason", "The AI could not confidently answer the question.")
            sources = parsed.get("sources", [])  # list[dict]
            draft_reply = parsed.get("draft_ticket_reply", "")
        except Exception as exc2:
            print(f"Fallback parsing also failed ({exc2}).")
            return (
                "I am sorry, but I was unable to process your "
                "request at this time."
            )

    # ==========================================
    # 7. CHECK ESCALATION DECISION
    # ==========================================

    if escalate:

        print("\nEscalation required.")

        # ==========================================
        # 8. SEND EMAIL TO ADMIN
        # ==========================================

        email_sent = send_escalation_email(
            customer_question=user_question,
            reason=reason
        )

        # ==========================================
        # 9. RETURN CUSTOMER RESPONSE
        # ==========================================

        if email_sent:
            base_msg = """
I am unable to provide a confident answer to your question
based on the available FMG support information.

I have forwarded your query to FMG Support for further
assistance. Our support team will review your request
and provide further assistance.
"""
        else:
            base_msg = """
I am unable to provide a confident answer to your question
based on the available FMG support information.

Your issue requires further investigation by FMG Support.
"""

        return base_msg + _format_draft_reply(draft_reply)

    # ==========================================
    # 10. IF NO ESCALATION, RETURN LLM ANSWER + CITED SOURCES + DRAFT REPLY
    # ==========================================

    return answer_text + _format_citations(sources) + _format_draft_reply(draft_reply)


# ==========================================
# RUN PROGRAM
# ==========================================

if __name__ == "__main__":
    run_frontend(answer_customer_question)

# if __name__ == "__main__":

#     question = input(
#         "Enter customer question: "
#     )

#     answer = answer_customer_question(
#         question
#     )

#     print("\n" + "=" * 60)
#     print("FMG AI CUSTOMER SUPPORT")
#     print("=" * 60)

#     print(answer)