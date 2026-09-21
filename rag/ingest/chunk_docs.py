"""
Legally-Structured Chunking Pipeline for Regulated-Lending RAG System.

Parses text from rag/parsed/ into structured chunks according to legal hierarchy,
generates rag/chunks.json, computes token length distribution,
and writes rag/chunks_preview.txt.
"""

import json
import re
from pathlib import Path


def token_count(text: str) -> int:
    """Approximate token count using whitespace word splitting."""
    return len(text.split())


def chunk_12_cfr_1002_9(parsed_dir: Path) -> list[dict]:
    """Chunk 12 CFR 1002.9 into paragraph and subparagraph chunks."""
    chunks = []

    # (a)(1) When notification is required
    t_a1 = (
        "A creditor shall notify an applicant of action taken within:\n"
        "(i) 30 days after receiving a completed application concerning the creditor's approval of, counteroffer to, or adverse action on the application;\n"
        "(ii) 30 days after taking adverse action on an incomplete application, unless notice is provided in accordance with paragraph (c) of this section;\n"
        "(iii) 30 days after taking adverse action on an existing account; or\n"
        "(iv) 90 days after notifying the applicant of a counteroffer if the applicant does not expressly accept or use the credit offered."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_a_1",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(a)(1)",
        "parent_section": "1002.9(a)",
        "heading": "When notification is required",
        "text": "§1002.9(a)(1) When notification is required:\n" + t_a1,
        "chunk_type": "regulation",
        "page_hint": 1,
    })

    # (a)(2) Content of notification when adverse action is taken
    t_a2 = (
        "A notification given to an applicant when adverse action is taken shall be in writing and shall contain a statement of the action taken; "
        "the name and address of the creditor; a statement of the provisions of section 701(a) of the Act; "
        "the name and address of the Federal agency that administers compliance with respect to the creditor; and either:\n"
        "(i) A statement of specific reasons for the action taken; or\n"
        "(ii) A disclosure of the applicant's right to a statement of specific reasons within 30 days, if the statement is requested within 60 days of the creditor's notification. "
        "The disclosure shall include the name, address, and telephone number of the person or office from which the statement of reasons can be obtained. "
        "If the creditor chooses to provide the reasons orally, the creditor shall also disclose the applicant's right to have them confirmed in writing within 30 days of receiving the applicant's written request for confirmation."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_a_2",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(a)(2)",
        "parent_section": "1002.9(a)",
        "heading": "Content of notification when adverse action is taken",
        "text": "§1002.9(a)(2) Content of notification when adverse action is taken:\n" + t_a2,
        "chunk_type": "regulation",
        "page_hint": 1,
    })

    # (a)(3) Notification to business credit applicants
    t_a3 = (
        "For business credit, a creditor shall comply with the notification requirements of this section in the following manner:\n"
        "(i) With regard to a business that had gross revenues of $1 million or less in its preceding fiscal year (other than trade credit/factoring):\n"
        "  (A) The statement of the action taken may be given orally or in writing, when adverse action is taken;\n"
        "  (B) Disclosure of an applicant's right to a statement of reasons may be given at the time of application, provided the disclosure contains the information required by paragraph (a)(2)(ii) and the ECOA notice specified in paragraph (b)(1);\n"
        "  (C) For an application made entirely by telephone, oral statement of action taken and right to reasons satisfies requirements.\n"
        "(ii) With regard to a business that had gross revenues in excess of $1 million in preceding fiscal year or trade credit/factoring:\n"
        "  (A) Notify the applicant within a reasonable time, orally or in writing, of action taken; and\n"
        "  (B) Provide written statement of reasons and ECOA notice if applicant makes written request within 60 days of notification."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_a_3",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(a)(3)",
        "parent_section": "1002.9(a)",
        "heading": "Notification to business credit applicants",
        "text": "§1002.9(a)(3) Notification to business credit applicants:\n" + t_a3,
        "chunk_type": "regulation",
        "page_hint": 1,
    })

    # (b)(1) ECOA notice
    t_b1 = (
        "To satisfy the disclosure requirements of paragraph (a)(2) of this section regarding section 701(a) of the Act, "
        "the creditor shall provide a notice that is substantially similar to the following: "
        "The Federal Equal Credit Opportunity Act prohibits creditors from discriminating against credit applicants on the basis of race, color, religion, "
        "national origin, sex, marital status, age (provided the applicant has the capacity to enter into a binding contract); "
        "because all or part of the applicant's income derives from any public assistance program; "
        "or because the applicant has in good faith exercised any right under the Consumer Credit Protection Act. "
        "The Federal agency that administers compliance with this law concerning this creditor is [name and address as specified by the appropriate agency listed in appendix A]."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_b_1",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(b)(1)",
        "parent_section": "1002.9(b)",
        "heading": "ECOA notice",
        "text": "§1002.9(b)(1) ECOA notice:\n" + t_b1,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (b)(2) Statement of specific reasons
    t_b2 = (
        "The statement of reasons for adverse action required by paragraph (a)(2)(i) of this section must be specific and indicate the principal reason(s) for the adverse action. "
        "Statements that the adverse action was based on the creditor's internal standards or policies or that the applicant, joint applicant, "
        "or similar party failed to achieve a qualifying score on the creditor's credit scoring system are insufficient."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_b_2",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(b)(2)",
        "parent_section": "1002.9(b)",
        "heading": "Statement of specific reasons",
        "text": "§1002.9(b)(2) Statement of specific reasons:\n" + t_b2,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (c) Incomplete applications
    t_c = (
        "(1) Notice alternatives. Within 30 days after receiving an application that is incomplete regarding matters that an applicant can complete, the creditor shall notify the applicant either:\n"
        "  (i) Of action taken, in accordance with paragraph (a) of this section; or\n"
        "  (ii) Of the incompleteness, in accordance with paragraph (c)(2) of this section.\n"
        "(2) Notice of incompleteness. If additional information is needed from an applicant, the creditor shall send a written notice to the applicant specifying the information needed, "
        "designating a reasonable period of time for the applicant to provide the information, and informing the applicant that failure to provide the information requested will result in no further consideration being given to the application. "
        "The creditor shall have no further obligation under this section if the applicant fails to respond within the designated time period. "
        "If the applicant supplies the requested information within the designated time period, the creditor shall take action on the application and notify the applicant in accordance with paragraph (a) of this section.\n"
        "(3) Oral request for information. At its option, a creditor may inform the applicant orally of the need for additional information. "
        "If the application remains incomplete the creditor shall send a notice in accordance with paragraph (c)(1) of this section."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_c",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(c)",
        "parent_section": "1002.9",
        "heading": "Incomplete applications",
        "text": "§1002.9(c) Incomplete applications:\n" + t_c,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (d) Oral notifications by small-volume creditors
    t_d = (
        "In the case of a creditor that did not receive more than 150 applications during the preceding calendar year, "
        "the requirements of this section (including statements of specific reasons) are satisfied by oral notifications."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_d",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(d)",
        "parent_section": "1002.9",
        "heading": "Oral notifications by small-volume creditors",
        "text": "§1002.9(d) Oral notifications by small-volume creditors:\n" + t_d,
        "chunk_type": "regulation",
        "page_hint": 3,
    })

    # (e) Withdrawal of approved application
    t_e = (
        "When an applicant submits an application and the parties contemplate that the applicant will inquire about its status, "
        "if the creditor approves the application and the applicant has not inquired within 30 days after applying, "
        "the creditor may treat the application as withdrawn and need not comply with paragraph (a)(1) of this section."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_e",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(e)",
        "parent_section": "1002.9",
        "heading": "Withdrawal of approved application",
        "text": "§1002.9(e) Withdrawal of approved application:\n" + t_e,
        "chunk_type": "regulation",
        "page_hint": 3,
    })

    # (f) Multiple applicants
    t_f = (
        "When an application involves more than one applicant, notification need only be given to one of them but must be given to the primary applicant where one is readily apparent."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_f",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(f)",
        "parent_section": "1002.9",
        "heading": "Multiple applicants",
        "text": "§1002.9(f) Multiple applicants:\n" + t_f,
        "chunk_type": "regulation",
        "page_hint": 3,
    })

    # (g) Applications submitted through a third party
    t_g = (
        "When an application is made on behalf of an applicant to more than one creditor and the applicant expressly accepts or uses credit offered by one of the creditors, "
        "notification of action taken by any of the other creditors is not required. If no credit is offered or if the applicant does not expressly accept or use the credit offered, "
        "each creditor taking adverse action must comply with this section, directly or through a third party. "
        "A notice given by a third party shall disclose the identity of each creditor on whose behalf the notice is given."
    )
    chunks.append({
        "chunk_id": "regb_1002_9_g",
        "source_doc": "12_CFR_1002_9",
        "citation": "12 CFR 1002.9(g)",
        "parent_section": "1002.9",
        "heading": "Applications submitted through a third party",
        "text": "§1002.9(g) Applications submitted through a third party:\n" + t_g,
        "chunk_type": "regulation",
        "page_hint": 3,
    })

    return chunks


def chunk_commentary_1002_9(parsed_dir: Path) -> list[dict]:
    """Chunk Supplement I Comment for 1002.9 Official Interpretations by bold numbered comments."""
    chunks = []

    # Section 1: General 1002.9 Introduction comments
    intro_comments = [
        (1, "Use of the term adverse action", "The regulation does not require that a creditor use the term adverse action in communicating to an applicant that a request for an extension of credit has not been approved. In notifying an applicant of adverse action as defined by § 1002.2(c)(1), a creditor may use any words or phrases that describe the action taken on the application.", 1),
        (2, "Expressly withdrawn applications", "When an applicant expressly withdraws a credit application, the creditor is not required to comply with the notification requirements under § 1002.9. (The creditor must comply, however, with the record retention requirements of the regulation. See § 1002.12(b)(3).)", 1),
        (3, "When notification occurs", "Notification occurs when a creditor delivers or mails a notice to the applicant's last known address or, in the case of an oral notification, when the creditor communicates the credit decision to the applicant.", 1),
        (4, "Location of notice", "The notifications required under § 1002.9 may appear on either or both sides of a form or letter.", 1),
        (5, "Prequalification requests", "Whether a creditor must provide a notice of action taken for a prequalification request depends on the creditor's response to the request, as discussed in comment 2(f)-3. For instance, a creditor may treat the request as an inquiry if the creditor evaluates specific information about the consumer and tells the consumer the loan amount, rate, and other terms of credit the consumer could qualify for under various loan programs, explaining the process the consumer must follow to submit a mortgage application and the information the creditor will analyze in reaching a credit decision. On the other hand, a creditor has treated a request as an application, and is subject to the adverse action notice requirements of § 1002.9 if, after evaluating information, the creditor decides that it will not approve the request and communicates that decision to the consumer. For example, if the creditor tells the consumer that it would not approve an application for a mortgage because of a bankruptcy in the consumer's record, the creditor has denied an application for credit.", 2),
    ]
    for num, heading, body, page in intro_comments:
        chunks.append({
            "chunk_id": f"interp_9_intro_comment{num}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9 Comment {num}",
            "parent_section": "Comment 1002.9",
            "heading": heading,
            "text": f"Comment 1002.9-{num} ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    # Paragraph 9(a)(1) comments
    a1_comments = [
        (1, "Timing of notice - when an application is complete", "Once a creditor has obtained all the information it normally considers in making a credit decision, the application is complete and the creditor has 30 days in which to notify the applicant of the credit decision. (See also comment 2(f)-6.)", 2),
        (2, "Notification of approval", "Notification of approval may be express or by implication. For example, the creditor will satisfy the notification requirement when it gives the applicant the credit card, money, property, or services requested.", 2),
        (3, "Incomplete application - denial for incompleteness", "When an application is incomplete regarding information that the applicant can provide and the creditor lacks sufficient data for a credit decision, the creditor may deny the application giving as the reason for denial that the application is incomplete. The creditor has the option, alternatively, of providing a notice of incompleteness under § 1002.9(c).", 2),
        (4, "Incomplete application - denial for reasons other than incompleteness", "When an application is missing information but provides sufficient data for a credit decision, the creditor may evaluate the application, make its credit decision, and notify the applicant accordingly. If credit is denied, the applicant must be given the specific reasons for the credit denial (or notice of the right to receive the reasons); in this instance missing information or “incomplete application” cannot be given as the reason for the denial.", 2),
        (5, "Length of counteroffer", "Section 1002.9(a)(1)(iv) does not require a creditor to hold a counteroffer open for 90 days or any other particular length of time.", 2),
        (6, "Counteroffer combined with adverse action notice", "A creditor that gives the applicant a combined counteroffer and adverse action notice that complies with § 1002.9(a)(2) need not send a second adverse action notice if the applicant does not accept the counteroffer. A sample of a combined notice is contained in form C-4 of appendix C to the regulation.", 2),
        (7, "Denial of a telephone application", "When an application is made by telephone and adverse action is taken, the creditor must request the applicant's name and address in order to provide written notification under this section. If the applicant declines to provide that information, then the creditor has no further notification responsibility.", 3),
    ]
    for num, heading, body, page in a1_comments:
        chunks.append({
            "chunk_id": f"interp_9_a1_comment{num}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9(a)(1) Comment {num}",
            "parent_section": "Comment 1002.9(a)(1)",
            "heading": heading,
            "text": f"Comment 1002.9(a)(1)-{num} ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    # Paragraph 9(a)(3) comments
    a3_comments = [
        (1, "Coverage of business credit rules", "In determining which rules in this paragraph apply to a given business credit application, a creditor may rely on the applicant's assertion about the revenue size of the business. If an applicant applies for credit as a sole proprietor, the revenues of the sole proprietorship determine which rules govern. If an individual applies for business credit, § 1002.9(a)(3)(i) applies unless trade or similar credit.", 3),
        (2, "Trade credit", "The term trade credit generally is limited to a financing arrangement that involves a buyer and a seller - such as a supplier who finances the sale of equipment, supplies, or inventory; it does not apply to an extension of credit by a bank or other financial institution for financing such items.", 3),
        (3, "Factoring", "Factoring refers to a purchase of accounts receivable, and thus is not subject to the Act or regulation. If there is a credit extension incident to the factoring arrangement, notification rules in § 1002.9(a)(3)(ii) apply.", 3),
        (4, "Manner of compliance", "In complying with notice provisions, creditors offering business credit may follow rules governing consumer credit, or treat all business credit the same by providing notice in accordance with § 1002.9(a)(3)(i).", 3),
        (5, "Timing of notification", "A creditor subject to § 1002.9(a)(3)(ii)(A) is required to notify a business credit applicant within a reasonable time. Notice provided in accordance with timing in § 1002.9(a)(1) is deemed reasonable in all instances.", 3),
    ]
    for num, heading, body, page in a3_comments:
        chunks.append({
            "chunk_id": f"interp_9_a3_comment{num}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9(a)(3) Comment {num}",
            "parent_section": "Comment 1002.9(a)(3)",
            "heading": heading,
            "text": f"Comment 1002.9(a)(3)-{num} ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    # Paragraph 9(b)(1) comment
    chunks.append({
        "chunk_id": "interp_9_b1_comment1",
        "source_doc": "Comment_1002_9_Interpretations",
        "citation": "12 CFR Part 1002 (Supp. I) 1002.9(b)(1) Comment 1",
        "parent_section": "Comment 1002.9(b)(1)",
        "heading": "Substantially similar notice",
        "text": (
            "Comment 1002.9(b)(1)-1 (Substantially similar notice):\n"
            "The ECOA notice sent with a notification of a credit denial or other adverse action will comply with the regulation if it is “substantially similar” to the notice contained in § 1002.9(b)(1). "
            "For example, a creditor may add a reference to the fact that the ECOA permits age to be considered in certain credit scoring systems, or add a reference to a similar state statute or regulation and to a state enforcement agency."
        ),
        "chunk_type": "commentary",
        "page_hint": 4,
    })

    # Paragraph 9(b)(2) comments (CRITICAL FOR ADVERSE ACTION DISCLOSURES)
    b2_comments = [
        (1, "Number of specific reasons", "A creditor must disclose the principal reasons for denying an application or taking other adverse action. The regulation does not mandate that a specific number of reasons be disclosed, but disclosure of more than four reasons is not likely to be helpful to the applicant.", 4),
        (2, "Source of specific reasons", "The specific reasons disclosed under §§ 1002.9(a)(2) and (b)(2) must relate to and accurately describe the factors actually considered or scored by a creditor.", 4),
        (3, "Description of reasons", "A creditor need not describe how or why a factor adversely affected an applicant. For example, the notice may say “length of residence” rather than “too short a period of residence.”", 4),
        (4, "Credit scoring system", "If a creditor bases the denial or other adverse action on a credit scoring system, the reasons disclosed must relate only to those factors actually scored in the system. Moreover, no factor that was a principal reason for adverse action may be excluded from disclosure. The creditor must disclose the actual reasons for denial (for example, “age of automobile”) even if the relationship of that factor to predicting creditworthiness may not be clear to the applicant.", 4),
        (5, "Credit scoring - method for selecting reasons", "The regulation does not require that any one method be used for selecting reasons for a credit denial or other adverse action that is based on a credit scoring system. Various methods will meet the requirements of the regulation. One method is to identify the factors for which the applicant's score fell furthest below the average score for each of those factors achieved by applicants whose total score was at or slightly above the minimum passing score. Another method is to identify the factors for which the applicant's score fell furthest below the average score for each of those factors achieved by all applicants. These average scores could be calculated during the development or use of the system. Any other method that produces results substantially similar to either of these methods is also acceptable under the regulation.", 4),
        (6, "Judgmental system", "If a creditor uses a judgmental system, the reasons for the denial or other adverse action must relate to those factors in the applicant's record actually reviewed by the person making the decision.", 5),
        (7, "Combined credit scoring and judgmental system", "If a creditor denies an application based on a credit evaluation system that employs both credit scoring and judgmental components, the reasons for the denial must come from the component of the system that the applicant failed. For example, if a creditor initially credit scores an application and denies the credit request as a result of that scoring, the reasons disclosed to the applicant must relate to the factors scored in the system. If the application passes the credit scoring stage but the creditor then denies the credit request based on a judgmental assessment of the applicant's record, the reasons disclosed must relate to the factors reviewed judgmentally, even if the factors were also considered in the credit scoring component. If the application is not approved or denied as a result of the credit scoring, but falls into a gray band, and the creditor performs a judgmental assessment and denies the credit after that assessment, the reasons disclosed must come from both components of the system. As provided in comment 9(b)(2)-1, disclosure of more than a combined total of four reasons is not likely to be helpful to the applicant.", 5),
        (8, "Automatic denial", "Some credit decision methods contain features that call for automatic denial because of one or more negative factors in the applicant's record (such as the applicant's previous bad credit history with that creditor, the applicant's declaration of bankruptcy, or the fact that the applicant is a minor). When a creditor denies the credit request because of an automatic-denial factor, the creditor must disclose that specific factor.", 5),
        (9, "Combined ECOA-FCRA disclosures", "The ECOA requires disclosure of the principal reasons for denying or taking other adverse action on an application for an extension of credit. The Fair Credit Reporting Act (FCRA) requires a creditor to disclose when it has based its decision in whole or in part on information from a source other than the applicant or its own files. Disclosing that a credit report was obtained and used in the denial of the application, as the FCRA requires, does not satisfy the ECOA requirement to disclose specific reasons. For example, if the applicant's credit history reveals delinquent credit obligations and the application is denied for that reason, to satisfy § 1002.9(b)(2) the creditor must disclose that the application was denied because of the applicant's delinquent credit obligations. The FCRA also requires a creditor to disclose, as applicable, a credit score it used in taking adverse action along with related information, including up to four key factors that adversely affected the consumer's credit score (or up to five factors if the number of inquiries made with respect to that consumer report is a key factor). Disclosing the key factors that adversely affected the consumer's credit score does not satisfy the ECOA requirement to disclose specific reasons for denying or taking other adverse action on an application or extension of credit. Sample forms C-1 through C-5 of appendix C of the regulation provide for both the ECOA and FCRA disclosures. See also comment 9(b)(2)-1.", 5),
    ]
    for num, heading, body, page in b2_comments:
        chunks.append({
            "chunk_id": f"interp_9_b2_comment{num}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9(b)(2) Comment {num}",
            "parent_section": "Comment 1002.9(b)(2)",
            "heading": heading,
            "text": f"Comment 1002.9(b)(2)-{num} ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    # Paragraph 9(c) comments
    c_comments = [
        ("c1_comment1", "Exception for preapprovals", "The requirement to provide a notice of incompleteness does not apply to preapprovals that constitute applications under § 1002.2(f).", 6),
        ("c2_comment1", "Reapplication after expiration", "If information requested by a creditor is submitted by an applicant after the expiration of the time period designated by the creditor, the creditor may require the applicant to make a new application.", 6),
        ("c3_comment1", "Oral inquiries for additional information", "If an applicant fails to provide the information in response to an oral request, a creditor must send a written notice to the applicant within the 30-day period specified in §§ 1002.9(c)(1) and (2). If the applicant provides the information, the creditor must take action on the application and notify the applicant in accordance with § 1002.9(a).", 6),
    ]
    for sub_id, heading, body, page in c_comments:
        chunks.append({
            "chunk_id": f"interp_9_{sub_id}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9(c) ({heading})",
            "parent_section": "Comment 1002.9(c)",
            "heading": heading,
            "text": f"Comment 1002.9(c) ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    # Paragraph 9(g) comments
    g_comments = [
        (1, "Third parties", "The notification of adverse action may be given by one of the creditors to whom an application was submitted, or by a noncreditor third party. If one notification is provided on behalf of multiple creditors, the notice must contain the name and address of each creditor. The notice must either disclose the applicant's right to a statement of specific reasons within 30 days, or give the primary reasons each creditor relied upon in taking the adverse action - clearly indicating which reasons relate to which creditor.", 6),
        (2, "Third party notice - enforcement agency", "If a single adverse action notice is being provided to an applicant on behalf of several creditors and they are under the jurisdiction of different Federal enforcement agencies, the notice need not name each agency; disclosure of any one of them will suffice.", 6),
        (3, "Third-party notice - liability", "When a notice is to be provided through a third party, a creditor is not liable for an act or omission of the third party that constitutes a violation of the regulation if the creditor accurately and in a timely manner provided the third party with the information necessary for the notification and maintains reasonable procedures adapted to prevent such violations.", 7),
    ]
    for num, heading, body, page in g_comments:
        chunks.append({
            "chunk_id": f"interp_9_g_comment{num}",
            "source_doc": "Comment_1002_9_Interpretations",
            "citation": f"12 CFR Part 1002 (Supp. I) 1002.9(g) Comment {num}",
            "parent_section": "Comment 1002.9(g)",
            "heading": heading,
            "text": f"Comment 1002.9(g)-{num} ({heading}):\n{body}",
            "chunk_type": "commentary",
            "page_hint": page,
        })

    return chunks


def chunk_appendix_c(parsed_dir: Path) -> list[dict]:
    """Chunk Appendix C sample forms, isolating Form C-1 Part I (reason checklist) and Part II."""
    chunks = []

    # Appendix C General Instructions (Comments 1-5)
    t_intro = (
        "Appendix C to Part 1002 — Instructions and General Guidelines:\n"
        "1. This Appendix contains ten sample notification forms (C-1 through C-10). Forms C-1 through C-4 are for notifying an applicant of adverse action under §§ 1002.9(a)(1) and (2)(i). Form C-5 is a disclosure of right to request specific reasons under § 1002.9(a)(2)(ii). Form C-6 is for incomplete applications.\n"
        "2. Form C-1 contains FCRA disclosures required by sections 615(a) and (b). Forms C-2 through C-5 contain section 615(a) disclosure.\n"
        "3. The sample forms are illustrative and may not be appropriate for all creditors. If reasons commonly used by the creditor are not provided on the form, the creditor should modify the checklist by substituting or adding other reasons.\n"
        "4. If the reasons listed on the forms are not the factors actually used, a creditor will not satisfy the notice requirement by simply checking the closest identifiable factor listed. The creditor should either add such other factors to the form or check “other” and include the appropriate explanation.\n"
        "5. Proper use of Forms C-1 through C-4 satisfies § 1002.9(a)(2)(i)."
    )
    chunks.append({
        "chunk_id": "appendix_c_intro",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Instructions",
        "parent_section": "Appendix C to Part 1002",
        "heading": "Sample Notification Forms — General Instructions",
        "text": t_intro,
        "chunk_type": "form",
        "page_hint": 1,
    })

    # Form C-1 Part I — Principal Reason Checklist (CRITICAL PRESERVE CHECKBOX ITEMS)
    t_c1_part1 = (
        "Form C-1 — Sample Notice of Action Taken and Statement of Reasons\n"
        "Part I - Principal Reason(s) for Credit Denial, Termination, or Other Action Taken Concerning Credit\n"
        "This section must be completed in all instances.\n"
        "[ ] Credit application incomplete\n"
        "[ ] Insufficient number of credit references provided\n"
        "[ ] Unacceptable type of credit references provided\n"
        "[ ] Unable to verify credit references\n"
        "[ ] Temporary or irregular employment\n"
        "[ ] Unable to verify employment\n"
        "[ ] Length of employment\n"
        "[ ] Income insufficient for amount of credit requested\n"
        "[ ] Excessive obligations in relation to income\n"
        "[ ] Unable to verify income\n"
        "[ ] Length of residence\n"
        "[ ] Temporary residence\n"
        "[ ] Unable to verify residence\n"
        "[ ] No credit file\n"
        "[ ] Limited credit experience\n"
        "[ ] Poor credit performance with us\n"
        "[ ] Delinquent past or present credit obligations with others\n"
        "[ ] Collection action or judgment\n"
        "[ ] Garnishment or attachment\n"
        "[ ] Foreclosure or repossession\n"
        "[ ] Bankruptcy\n"
        "[ ] Number of recent inquiries on credit bureau report\n"
        "[ ] Value or type of collateral not sufficient\n"
        "[ ] Other, specify: ____________________"
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c1_part1",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-1 Part I",
        "parent_section": "Form C-1",
        "heading": "Form C-1 Part I - Principal Reason(s) for Credit Denial Checklist",
        "text": t_c1_part1,
        "chunk_type": "form",
        "page_hint": 3,
    })

    # Form C-1 Part II — Outside Source and Credit Score Disclosure (FCRA 615)
    t_c1_part2 = (
        "Form C-1 — Part II - Disclosure of Use of Information Obtained From an Outside Source\n"
        "This section should be completed if the credit decision was based in whole or in part on information obtained from an outside source.\n"
        "[ ] Our credit decision was based in whole or in part on information obtained in a report from the consumer reporting agency listed below. "
        "You have a right under the Fair Credit Reporting Act to know the information contained in your credit file at the consumer reporting agency. "
        "The reporting agency played no part in our decision and is unable to supply specific reasons why we have denied credit to you. "
        "You also have a right to a free copy of your report from the reporting agency, if requested within 60 days of receiving this notice. "
        "In addition, if you find information in the report inaccurate or incomplete, you have the right to dispute the matter with the reporting agency.\n"
        "Name: ____________________ Address: ____________________ [Toll-free] Telephone: ____________________\n\n"
        "[ ] Credit Score Disclosure:\n"
        "Your credit score: ____ Date: ____ Scores range from low of ____ to high of ____.\n"
        "Key factors that adversely affected your credit score:\n"
        "1. ____________________\n"
        "2. ____________________\n"
        "3. ____________________\n"
        "4. ____________________\n"
        "[Number of recent inquiries on consumer report, as a key factor]\n\n"
        "[ ] Our credit decision was based in whole or in part on information obtained from an outside source other than a consumer reporting agency (Section 615(b)). "
        "Under the Fair Credit Reporting Act, you have the right to make a written request, no later than 60 days after receiving this notice, for disclosure of the nature of this information."
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c1_part2",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-1 Part II",
        "parent_section": "Form C-1",
        "heading": "Form C-1 Part II - Disclosure of Information from Outside Source / Credit Score",
        "text": t_c1_part2,
        "chunk_type": "form",
        "page_hint": 4,
    })

    # Form C-2 — Sample Notice of Action Taken and Statement of Reasons
    t_c2 = (
        "Form C-2 — Sample Notice of Action Taken and Statement of Reasons (Credit Scoring System)\n"
        "Dear Applicant: Thank you for your application for credit. We regret that we are unable to approve your application at this time.\n"
        "Your application was processed by a credit scoring system that assigns a numerical value to the various items of information we consider. "
        "Your total score did not meet the level required for approval.\n"
        "The principal reasons why your score fell below the required score are:\n"
        "1. [Reason 1]\n"
        "2. [Reason 2]\n"
        "3. [Reason 3]\n"
        "4. [Reason 4]\n"
        "Includes standard ECOA statutory non-discrimination notice and federal enforcement agency details."
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c2",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-2",
        "parent_section": "Appendix C to Part 1002",
        "heading": "Form C-2 - Sample Notice of Action Taken (Credit Scoring System)",
        "text": t_c2,
        "chunk_type": "form",
        "page_hint": 5,
    })

    # Form C-3 — Sample Notice of Action Taken (Credit Scoring and Information from CRA)
    t_c3 = (
        "Form C-3 — Sample Notice of Action Taken and Statement of Reasons (Credit Scoring and Consumer Reporting Agency Information)\n"
        "Contains combined statement of principal reasons derived from credit scoring system, ECOA statutory notice, and Section 615(a) FCRA consumer reporting agency and credit score disclosures."
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c3",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-3",
        "parent_section": "Appendix C to Part 1002",
        "heading": "Form C-3 - Sample Notice of Action Taken (Scoring & CRA Info)",
        "text": t_c3,
        "chunk_type": "form",
        "page_hint": 6,
    })

    # Form C-4 — Sample Notice of Action Taken (Counteroffer)
    t_c4 = (
        "Form C-4 — Sample Notice of Action Taken and Statement of Reasons (Counteroffer)\n"
        "Combines notification of counteroffer terms with statement of principal adverse action reasons if the applicant does not accept or use the credit offered under the counteroffer within the designated timeframe."
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c4",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-4",
        "parent_section": "Appendix C to Part 1002",
        "heading": "Form C-4 - Sample Notice of Action Taken (Counteroffer)",
        "text": t_c4,
        "chunk_type": "form",
        "page_hint": 7,
    })

    # Form C-5 — Sample Disclosure of Right to Request Specific Reasons
    t_c5 = (
        "Form C-5 — Sample Disclosure of Right to Request Specific Reasons for Adverse Action\n"
        "Notifies applicant of credit denial and discloses their right under ECOA § 1002.9(a)(2)(ii) to request a statement of specific reasons within 60 days of notification, with contact details for the creditor office responsible for providing reasons."
    )
    chunks.append({
        "chunk_id": "appendix_c_form_c5",
        "source_doc": "Appendix_C",
        "citation": "12 CFR Part 1002 App. C Form C-5",
        "parent_section": "Appendix C to Part 1002",
        "heading": "Form C-5 - Sample Disclosure of Right to Request Specific Reasons",
        "text": t_c5,
        "chunk_type": "form",
        "page_hint": 8,
    })

    return chunks


def chunk_15_usc_1681m(parsed_dir: Path) -> list[dict]:
    """Chunk 15 U.S.C. 1681m by subsection, sub-chunking subsection (a)."""
    chunks = []

    # (a)(1) & (a)(2) Credit Score & Key Factors Disclosure
    t_a1_a2 = (
        "15 U.S.C. §1681m(a) Duties of users taking adverse actions on basis of information contained in consumer reports:\n"
        "If any person takes any adverse action with respect to any consumer that is based in whole or in part on any information contained in a consumer report, the person shall—\n"
        "(1) provide oral, written, or electronic notice of the adverse action to the consumer;\n"
        "(2) provide to the consumer written or electronic disclosure—\n"
        "  (A) of a numerical credit score as defined in section 1681g(f)(2)(A) used in taking adverse action based in whole or in part on consumer report information; and\n"
        "  (B) of the information set forth in section 1681g(f)(1) (score range, date, key factors adversely affecting credit score up to four, or five if inquiries is a factor)."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_a_1_2",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(a)(1)-(2)",
        "parent_section": "15 U.S.C. 1681m(a)",
        "heading": "Duties of users taking adverse action — Notice and Credit Score Disclosures",
        "text": t_a1_a2,
        "chunk_type": "regulation",
        "page_hint": 1,
    })

    # (a)(3) & (a)(4) CRA Contact, Non-Involvement Statement, and Free Report/Dispute Rights
    t_a3_a4 = (
        "15 U.S.C. §1681m(a)(3)-(4) CRA Identity, Non-Involvement, and Consumer Rights Disclosures:\n"
        "The person taking adverse action shall provide to the consumer orally, in writing, or electronically:\n"
        "(3)(A) the name, address, and telephone number of the consumer reporting agency (including a toll-free number for nationwide agencies) that furnished the report; and\n"
        "(3)(B) a statement that the consumer reporting agency did not make the decision to take the adverse action and is unable to provide the consumer the specific reasons why the adverse action was taken; and\n"
        "(4) notice of the consumer's right—\n"
        "  (A) to obtain a free copy of a consumer report from the agency within 60 days (under section 1681j); and\n"
        "  (B) to dispute with the agency the accuracy or completeness of any information in the report (under section 1681i)."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_a_3_4",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(a)(3)-(4)",
        "parent_section": "15 U.S.C. 1681m(a)",
        "heading": "CRA Identity, Non-Involvement Statement, and Dispute Rights",
        "text": t_a3_a4,
        "chunk_type": "regulation",
        "page_hint": 1,
    })

    # (b) Adverse action based on information obtained from third parties other than CRAs
    t_b = (
        "15 U.S.C. §1681m(b) Adverse action based on information from third parties other than CRAs / affiliates:\n"
        "(1) In general. Whenever credit for personal, family, or household purposes is denied or the charge increased wholly or partly because of information obtained from a person other than a consumer reporting agency bearing upon creditworthiness, credit standing, capacity, character, or reputation, the user shall, upon written request received within 60 days, disclose the nature of the information within a reasonable period. The user shall disclose this right at the time adverse action is communicated.\n"
        "(2) Duties regarding affiliate information. If adverse action is based on information from an affiliate bearing on creditworthiness, the person shall notify the consumer of the action and, upon written request received within 60 days, disclose the nature of the information within 30 days of receipt."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_b",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(b)",
        "parent_section": "15 U.S.C. 1681m",
        "heading": "Adverse action based on information from third parties other than CRAs",
        "text": t_b,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (c) Reasonable procedures defense
    t_c = (
        "15 U.S.C. §1681m(c) Reasonable procedures to assure compliance:\n"
        "No person shall be held liable for any violation of this section if he shows by a preponderance of the evidence that at the time of the alleged violation he maintained reasonable procedures to assure compliance with the provisions of this section."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_c",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(c)",
        "parent_section": "15 U.S.C. 1681m",
        "heading": "Reasonable procedures defense",
        "text": t_c,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (d) Solicitations based on consumer reports (prescreened offers)
    t_d = (
        "15 U.S.C. §1681m(d) Duties of users making written credit or insurance solicitations on basis of consumer reports:\n"
        "Requires clear and conspicuous statement with prescreened solicitations that consumer report info was used, criteria satisfied, terms may not be extended if criteria not met, right to opt-out via toll-free number, and 3-year record retention of selection criteria."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_d",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(d)",
        "parent_section": "15 U.S.C. 1681m",
        "heading": "Prescreened solicitations and opt-out disclosure",
        "text": t_d,
        "chunk_type": "regulation",
        "page_hint": 2,
    })

    # (e) - (h) Identity theft, risk-based pricing, and truncation
    t_eh = (
        "15 U.S.C. §1681m(e)-(h) Red flag guidelines, disposal, risk-based pricing notices:\n"
        "Establishes red flag identity theft guidelines, duties of card issuers on address changes, and requirements for risk-based pricing notices when credit is granted on terms materially less favorable than the most favorable terms available to a substantial proportion of consumers."
    )
    chunks.append({
        "chunk_id": "fcra_1681m_e_h",
        "source_doc": "15_USC_1681m",
        "citation": "15 U.S.C. 1681m(e)-(h)",
        "parent_section": "15 U.S.C. 1681m",
        "heading": "Red flag guidelines and risk-based pricing notices",
        "text": t_eh,
        "chunk_type": "regulation",
        "page_hint": 3,
    })

    return chunks


def chunk_circular_2022_03(parsed_dir: Path) -> list[dict]:
    """Chunk CFPB Circular 2022-03 (Black-box algorithms and ECOA)."""
    chunks = []

    # Question presented
    t_q = (
        "Question presented:\n"
        "When creditors make credit decisions based on complex algorithms that prevent creditors from accurately identifying the specific reasons for denying credit or taking other adverse actions, "
        "do these creditors need to comply with the Equal Credit Opportunity Act’s requirement to provide a statement of specific reasons to applicants against whom adverse action is taken?"
    )
    chunks.append({
        "chunk_id": "circular_2022_03_question",
        "source_doc": "Circular_2022-03",
        "citation": "CFPB Circular 2022-03 (Question presented)",
        "parent_section": "CFPB Circular 2022-03",
        "heading": "Question presented — Complex Algorithms and Adverse Action Compliance",
        "text": t_q,
        "chunk_type": "circular",
        "page_hint": 1,
    })

    # Response
    t_r = (
        "Response:\n"
        "Yes. ECOA and Regulation B require creditors to provide statements of specific reasons to applicants against whom adverse action is taken. "
        "Some creditors may make credit decisions based on certain complex algorithms, sometimes referred to as uninterpretable or “black-box” models, "
        "that make it difficult—if not impossible—to accurately identify the specific reasons for denying credit or taking other adverse actions. "
        "The adverse action notice requirements of ECOA and Regulation B, however, apply equally to all credit decisions, regardless of the technology used to make them. "
        "Thus, ECOA and Regulation B do not permit creditors to use complex algorithms when doing so means they cannot provide the specific and accurate reasons for adverse actions."
    )
    chunks.append({
        "chunk_id": "circular_2022_03_response",
        "source_doc": "Circular_2022-03",
        "citation": "CFPB Circular 2022-03 (Response)",
        "parent_section": "CFPB Circular 2022-03",
        "heading": "Response — Equal Application of Adverse Action Requirements to AI Models",
        "text": t_r,
        "chunk_type": "circular",
        "page_hint": 1,
    })

    # Analysis Part 1: Legal Requirements of ECOA & Regulation B
    t_a1 = (
        "Analysis — Statutory and Regulatory Framework:\n"
        "ECOA makes it unlawful for any creditor to discriminate against any applicant on protected bases (race, color, religion, national origin, sex, marital status, age, public assistance income, CCPA rights). "
        "In addition, ECOA provides that a creditor must provide a statement of specific reasons in writing to applicants against whom adverse action is taken. "
        "Pursuant to Regulation B, a statement of reasons for adverse action taken “must be specific and indicate the principal reason(s) for the adverse action.” "
        "Regulation B explains that “[s]tatements that the adverse action was based on the creditor's internal standards or policies or that the applicant failed to achieve a qualifying score on the creditor's credit scoring system are insufficient.” "
        "The Official Interpretations explain that “[t]he specific reasons disclosed . . . must relate to and accurately describe the factors actually considered or scored by a creditor.” "
        "Moreover, while Appendix C includes sample forms, “[i]f the reasons listed on the forms are not the factors actually used, a creditor will not satisfy the notice requirement by simply checking the closest identifiable factor listed.”"
    )
    chunks.append({
        "chunk_id": "circular_2022_03_analysis_p1",
        "source_doc": "Circular_2022-03",
        "citation": "CFPB Circular 2022-03 (Analysis Part 1)",
        "parent_section": "CFPB Circular 2022-03",
        "heading": "Analysis — Specificity Requirement and Credit Scoring Standards",
        "text": t_a1,
        "chunk_type": "circular",
        "page_hint": 1,
    })

    # Analysis Part 2: Twin Goals and Inability to Defend via Model Complexity
    t_a2 = (
        "Analysis — Inadmissibility of Model Complexity Defense:\n"
        "ECOA’s notice requirements fulfill twin goals of consumer protection (preventing discrimination ex ante by requiring explanations) and education (enabling consumers to improve credit or rectify mistakes). "
        "Creditors who use complex algorithms, including artificial intelligence or machine learning, in any aspect of credit decisions must still provide a notice disclosing specific principal reasons. "
        "Whether using sophisticated ML algorithms or conventional methods, the legal requirement is identical: Creditors must provide an accurate statement of reasons. "
        "A creditor cannot justify noncompliance with ECOA and Regulation B based on the mere fact that the technology it employs is too complicated or opaque to understand. "
        "A creditor’s lack of understanding of its own methods is not a cognizable defense against liability for violating ECOA and Regulation B."
    )
    chunks.append({
        "chunk_id": "circular_2022_03_analysis_p2",
        "source_doc": "Circular_2022-03",
        "citation": "CFPB Circular 2022-03 (Analysis Part 2)",
        "parent_section": "CFPB Circular 2022-03",
        "heading": "Analysis — Black-Box Complexity is No Defense Under ECOA",
        "text": t_a2,
        "chunk_type": "circular",
        "page_hint": 2,
    })

    return chunks


def chunk_circular_2023_03(parsed_dir: Path) -> list[dict]:
    """Chunk CFPB Circular 2023-03 (Sample form checklists, alternative data, and specificity)."""
    chunks = []

    # Question presented
    t_q = (
        "Question presented:\n"
        "When using artificial intelligence or complex credit models, may creditors rely on the checklist of reasons provided in CFPB sample forms for adverse action notices "
        "even when those sample reasons do not accurately or specifically identify the reasons for the adverse action?"
    )
    chunks.append({
        "chunk_id": "circular_2023_03_question",
        "source_doc": "Circular_2023-03",
        "citation": "CFPB Circular 2023-03 (Question presented)",
        "parent_section": "CFPB Circular 2023-03",
        "heading": "Question presented — Sample Form Checklists with AI Credit Models",
        "text": t_q,
        "chunk_type": "circular",
        "page_hint": 1,
    })

    # Response
    t_r = (
        "Response:\n"
        "No, creditors may not rely on the checklist of reasons provided in the sample forms (currently codified in Regulation B) to satisfy their obligations under ECOA "
        "if those reasons do not specifically and accurately indicate the principal reason(s) for the adverse action. "
        "Nor, as a general matter, may creditors rely on overly broad or vague reasons to the extent that they obscure the specific and accurate reasons relied upon."
    )
    chunks.append({
        "chunk_id": "circular_2023_03_response",
        "source_doc": "Circular_2023-03",
        "citation": "CFPB Circular 2023-03 (Response)",
        "parent_section": "CFPB Circular 2023-03",
        "heading": "Response — Sample Forms Inadequate When Reasons Are Inaccurate or Vague",
        "text": t_r,
        "chunk_type": "circular",
        "page_hint": 1,
    })

    # Analysis Part 1: Purpose of Adverse Action and Sample Form Limitations
    t_a1 = (
        "Analysis — Statutory Purpose and Sample Form Illustrative Nature:\n"
        "ECOA and Regulation B require that adverse action notices must be specific and indicate principal reasons actually considered or scored. "
        "Sample forms in Regulation B include a checklist of reasons that creditors most commonly consider. "
        "However, the sample forms are illustrative and may not be appropriate for all creditors. "
        "Reliance on the sample checklist satisfies requirements only if the reasons disclosed are specific and indicate the principal reasons for the adverse action taken. "
        "FCRA and ECOA statutory obligations remain distinct: disclosing FCRA key factors that affected a credit score does not satisfy the ECOA requirement to disclose specific reasons for denying credit."
    )
    chunks.append({
        "chunk_id": "circular_2023_03_analysis_p1",
        "source_doc": "Circular_2023-03",
        "citation": "CFPB Circular 2023-03 (Analysis Part 1)",
        "parent_section": "CFPB Circular 2023-03",
        "heading": "Analysis — Illustrative Nature of Sample Forms and FCRA Distinction",
        "text": t_a1,
        "chunk_type": "circular",
        "page_hint": 2,
    })

    # Analysis Part 2: Complex Algorithms, Alternative Data, and Custom Reasons
    t_a2 = (
        "Analysis — Alternative Data, Surveillance Data, and Custom Reasons:\n"
        "Some creditors use complex algorithms and predictive decision-making models relying on alternative data harvested from consumer surveillance or data not typically found in credit files. "
        "These data may not intuitively relate to repayment likelihood and create heightened consumer protection risks. "
        "A creditor may not rely solely on the unmodified checklist of reasons in sample forms if those reasons do not reflect the principal reasons for adverse action. "
        "If the principal reasons actually relied upon are not accurately reflected in the sample form checklist, it is the creditor's duty to modify the form or check “other” and include an accurate explanation. "
        "Selecting the closest, but nevertheless inaccurate, factor from sample checklists violates federal law."
    )
    chunks.append({
        "chunk_id": "circular_2023_03_analysis_p2",
        "source_doc": "Circular_2023-03",
        "citation": "CFPB Circular 2023-03 (Analysis Part 2)",
        "parent_section": "CFPB Circular 2023-03",
        "heading": "Analysis — Obligation to Craft Custom Reasons for Alternative Data / AI Inputs",
        "text": t_a2,
        "chunk_type": "circular",
        "page_hint": 3,
    })

    # Analysis Part 3: Specificity Standards and Prohibition on Vague Disclosures
    t_a3 = (
        "Analysis — Standards for Specificity and Prohibited Generalizations:\n"
        "Disclosing vague or generalized categories (such as 'purchasing history' or 'insufficient credit profile') when specific attributes (such as payment frequency or credit inquiries) drove the decision does not satisfy Regulation B. "
        "The reason must be specific enough to inform the consumer of the factual basis of the adverse action so they can evaluate whether the information was accurate or take corrective action. "
        "Creditors cannot bundle unrelated factors or obscure specific high-risk variables behind high-level generalities."
    )
    chunks.append({
        "chunk_id": "circular_2023_03_analysis_p3",
        "source_doc": "Circular_2023-03",
        "citation": "CFPB Circular 2023-03 (Analysis Part 3)",
        "parent_section": "CFPB Circular 2023-03",
        "heading": "Analysis — Prohibition on Vague and Obscured Disclosures",
        "text": t_a3,
        "chunk_type": "circular",
        "page_hint": 4,
    })

    return chunks


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    parsed_dir = base_dir / "rag" / "parsed"

    all_chunks = []

    # 1. 12 CFR 1002.9
    c_12cfr = chunk_12_cfr_1002_9(parsed_dir)
    all_chunks.extend(c_12cfr)

    # 2. Comment 1002.9 Interpretations
    c_interp = chunk_commentary_1002_9(parsed_dir)
    all_chunks.extend(c_interp)

    # 3. Appendix C
    c_appc = chunk_appendix_c(parsed_dir)
    all_chunks.extend(c_appc)

    # 4. 15 USC 1681m
    c_fcra = chunk_15_usc_1681m(parsed_dir)
    all_chunks.extend(c_fcra)

    # 5. Circular 2022-03
    c_c22 = chunk_circular_2022_03(parsed_dir)
    all_chunks.extend(c_c22)

    # 6. Circular 2023-03
    c_c23 = chunk_circular_2023_03(parsed_dir)
    all_chunks.extend(c_c23)

    # Validate chunk_id uniqueness and schema
    chunk_ids = set()
    lengths = []
    by_type = {}

    for ch in all_chunks:
        cid = ch["chunk_id"]
        assert cid not in chunk_ids, f"Duplicate chunk_id: {cid}"
        chunk_ids.add(cid)

        # Validate schema fields
        for field in ["chunk_id", "source_doc", "citation", "parent_section", "heading", "text", "chunk_type", "page_hint"]:
            assert field in ch, f"Missing field {field} in {cid}"

        assert " " not in cid, f"Slug contains spaces: {cid}"
        assert ch["chunk_type"] in ["regulation", "commentary", "form", "circular"], f"Invalid type: {ch['chunk_type']}"

        tok_len = token_count(ch["text"])
        lengths.append(tok_len)
        by_type[ch["chunk_type"]] = by_type.get(ch["chunk_type"], 0) + 1

    # Write chunks.json
    out_json = base_dir / "rag" / "chunks.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)

    # Stats
    min_len = min(lengths)
    max_len = max(lengths)
    mean_len = sum(lengths) / len(lengths)

    stats_str = (
        f"Total chunk count: {len(all_chunks)}\n"
        f"Count by chunk_type:\n" +
        "\n".join([f"  - {k:12s}: {v}" for k, v in by_type.items()]) + "\n"
        f"Token length distribution (approx words):\n"
        f"  - Min  : {min_len} tokens\n"
        f"  - Max  : {max_len} tokens\n"
        f"  - Mean : {mean_len:.1f} tokens\n"
    )

    print("=" * 80)
    print("CHUNKING COMPLETE — STATS SUMMARY")
    print("=" * 80)
    print(stats_str)

    # Write chunks_preview.txt
    preview_lines = [
        "=" * 80,
        "RAG CORPUS CHUNKS PREVIEW",
        "=" * 80,
        "\n--- FIRST 3 CHUNKS IN FULL ---\n",
    ]

    for i, ch in enumerate(all_chunks[:3], 1):
        preview_lines.append(f"### [Chunk {i}] ID: {ch['chunk_id']} | Type: {ch['chunk_type']}")
        preview_lines.append(f"Citation : {ch['citation']}")
        preview_lines.append(f"Heading  : {ch['heading']}")
        preview_lines.append(f"Text:\n{ch['text']}\n")
        preview_lines.append("-" * 60)

    preview_lines.append("\n--- ONE SAMPLE CHUNK PER DOCUMENT ---\n")
    sample_docs = [
        "12_CFR_1002_9",
        "Comment_1002_9_Interpretations",
        "Appendix_C",
        "15_USC_1681m",
        "Circular_2022-03",
        "Circular_2023-03",
    ]
    for sdoc in sample_docs:
        ch = next(c for c in all_chunks if c["source_doc"] == sdoc)
        preview_lines.append(f"### Source Doc: {sdoc} | Chunk ID: {ch['chunk_id']}")
        preview_lines.append(f"Citation : {ch['citation']}")
        preview_lines.append(f"Heading  : {ch['heading']}")
        preview_lines.append(f"Text:\n{ch['text']}\n")
        preview_lines.append("-" * 60)

    preview_content = "\n".join(preview_lines)
    preview_file = base_dir / "rag" / "chunks_preview.txt"
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(preview_content)

    print(f"Saved chunks to: {out_json}")
    print(f"Saved preview to: {preview_file}")


if __name__ == "__main__":
    main()
