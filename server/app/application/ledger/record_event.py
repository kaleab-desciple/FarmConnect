from app.domain.ledger.entities import LedgerEvent
from app.infrastructure.repositories.ledger_repo import LedgerRepository
from app.infrastructure.repositories.account_repo import AccountRepository
from app.infrastructure.repositories.journal_repo import JournalRepository
from app.application.accounting.ledger_to_journal_mapper import LedgerToJournalMapper
from app.application.accounting.post_journal_entry import PostJournalEntry, PostJournalEntryRequest
from app.domain.ledger.entities import ReferenceType


class RecordLedgerEventUseCase:
    def __init__(self, ledger_repo: LedgerRepository, account_repo: AccountRepository, journal_repo: JournalRepository):
        self.ledger_repo = ledger_repo
        self.account_repo = account_repo
        self.journal_repo = journal_repo
        self.mapper = LedgerToJournalMapper(account_repo)
        self.post_journal_uc = PostJournalEntry(journal_repo, account_repo)

    def execute(self, event: LedgerEvent) -> LedgerEvent:
        """Record a ledger event (append-only) and create corresponding journal entry."""
        # Record the ledger event
        recorded_event = self.ledger_repo.append(event)

        # Map to journal lines and post journal entry
        lines = self.mapper.map_event_to_journal_lines(event)
        if lines:
            ref_type = ReferenceType(event.reference_type.value)
            request = PostJournalEntryRequest(
                reference_type=ref_type,
                reference_id=event.reference_id,
                description=f"{event.event_type.value} for {event.reference_type.value} {event.reference_id}",
                lines=lines
            )
            self.post_journal_uc.execute(request)

        return recorded_event