"""
Database adapter to convert between database models and application models
"""
from app.database.models import Conversation as DBConversation, LoanApplication as DBLoanApplication, Message
from app.models import ConversationState, Message

def db_conversation_to_state(db_conv: DBConversation) -> "ConversationState":
    """Convert database Conversation to ConversationState"""
    from app.models import LoanApplication
    messages = [
        Message(
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in sorted(db_conv.messages, key=lambda x: x.timestamp)
    ]

    loan_application = None
    if db_conv.loan_application:
        loan_application = LoanApplication(
            name=db_conv.loan_application.name,
            loan_amount=db_conv.loan_application.loan_amount,
            loan_purpose=db_conv.loan_application.loan_purpose,
            monthly_salary=db_conv.loan_application.monthly_salary,
            employment_type=db_conv.loan_application.employment_type,
            credit_score=db_conv.loan_application.credit_score,
            existing_loans=db_conv.loan_application.existing_loans,
        )

    return ConversationState(
        conversation_id=db_conv.id,
        stage=db_conv.stage,
        messages=messages,
        loan_application=loan_application,
        documents={doc.doc_type: doc.filename for doc in db_conv.documents},
        decision=db_conv.decision
    )

def state_to_db_conversation(state: "ConversationState", db_conv: DBConversation = None) -> DBConversation:
    """Convert ConversationState to database Conversation"""
    if db_conv is None:
        db_conv = DBConversation(
            id=state.conversation_id,
            stage=state.stage,
            decision=state.decision
        )
    else:
        db_conv.stage = state.stage
        db_conv.decision = state.decision

    if state.loan_application:
        if not db_conv.loan_application:
            db_conv.loan_application = DBLoanApplication()
        db_conv.loan_application.name = state.loan_application.name
        db_conv.loan_application.loan_amount = state.loan_application.loan_amount
        db_conv.loan_application.loan_purpose = state.loan_application.loan_purpose
        db_conv.loan_application.monthly_salary = state.loan_application.monthly_salary
        db_conv.loan_application.employment_type = state.loan_application.employment_type
        db_conv.loan_application.credit_score = state.loan_application.credit_score
        db_conv.loan_application.existing_loans = state.loan_application.existing_loans

    return db_conv


