from typing import Protocol, List
from app.domain.accounting.entities import JournalEntry, ReferenceType


class JournalRepository(Protocol):
    def get_by_reference(self, reference_type: str, reference_id: str) -> List[JournalEntry]:
        ...


class GetJournalEntriesByReferenceRequest:
    def __init__(self, reference_type: str, reference_id: str):
        self.reference_type = reference_type
        self.reference_id = reference_id


class GetJournalEntriesByReference:
    def __init__(self, journal_repo: JournalRepository):
        self.journal_repo = journal_repo

    def execute(self, request: GetJournalEntriesByReferenceRequest) -> List[JournalEntry]:
        return self.journal_repo.get_by_reference(request.reference_type, request.reference_id)
