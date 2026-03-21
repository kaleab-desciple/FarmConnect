// FarmConnect User Types - Mirroring Python DTOs from shared_models
import { OnboardingStatus, UserRole } from "./enums";

/**
 * User model - represents a platform user
 */
export interface User {
  id: string;
  keycloak_id?: string;
  role: UserRole;
  name: string;
  email: string;
  phone?: string;
  created_at: string; // ISO datetime
  metadata?: Record<string, unknown>;
  onboarding_status?: OnboardingStatus;
  onboarding_agent_id?: string;
}

/**
 * User creation request
 */
export interface UserCreate {
  keycloak_id?: string;
  role: UserRole;
  name: string;
  email: string;
  phone?: string;
  metadata?: Record<string, unknown>;
  onboarding_status?: OnboardingStatus;
  onboarding_agent_id?: string;
}

/**
 * User update request
 */
export interface UserUpdate {
  role?: UserRole;
  name?: string;
  email?: string;
  phone?: string;
  metadata?: Record<string, unknown>;
  onboarding_status?: OnboardingStatus;
  onboarding_agent_id?: string;
}

/**
 * Paginated user list response
 */
export interface UserListResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * User profile for display
 */
export interface UserProfile {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: UserRole;
  avatar_url?: string;
  created_at: string;
}
