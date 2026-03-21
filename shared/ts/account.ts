// FarmConnect Accounting Types - Mirroring Python DTOs from shared_models
import { AccountType, OwnerType } from "./enums";

/**
 * Account model
 */
export interface Account {
  id: string;
  owner_type: OwnerType;
  owner_id: string;
  account_type: AccountType;
  name: string;
  currency: string;
  created_at: string;
}

/**
 * Account creation request
 */
export interface AccountCreate {
  owner_type: OwnerType;
  owner_id: string;
  account_type: AccountType;
  name: string;
  currency?: string;
}

/**
 * Account balance response
 */
export interface AccountBalance {
  account_id: string;
  balance: number;
  currency: string;
  as_of: string;
}

/**
 * Journal entry model
 */
export interface JournalEntry {
  id: string;
  reference_type?: string;
  reference_id?: string;
  description?: string;
  created_at: string;
}

/**
 * Journal entry creation request
 */
export interface JournalEntryCreate {
  reference_type?: string;
  reference_id?: string;
  description: string;
  lines: JournalLineCreate[];
}

/**
 * Journal line model
 */
export interface JournalLine {
  id: number;
  journal_entry_id: string;
  account_id: string;
  debit_amount: number;
  credit_amount: number;
}

/**
 * Journal line creation request
 */
export interface JournalLineCreate {
  account_id: string;
  debit_amount: number;
  credit_amount: number;
}

/**
 * Ledger event model
 */
export interface LedgerEvent {
  id: string;
  aggregate_type: string;
  aggregate_id: string;
  event_type: string;
  amount: number;
  currency: string;
  direction: string;
  reference_type: string;
  reference_id: string;
  event_metadata?: Record<string, unknown>;
  created_at: string;
}
