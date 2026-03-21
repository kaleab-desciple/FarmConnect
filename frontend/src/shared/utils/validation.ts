import { z } from 'zod';

/**
 * Shared validation schemas used across the application to ensure
 * consistency between frontend forms and backend DTOs.
 */

// ============ Auth Schemas ============

export const loginSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const registerSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  phone: z.string().optional(),
});

// ============ Farm Schemas ============

export const farmCreateSchema = z.object({
  name: z.string().min(3, 'Farm name must be at least 3 characters'),
  location_lat: z.number({ required_error: 'Please pin your location on the map' }),
  location_lng: z.number({ required_error: 'Please pin your location on the map' }),
  location_address: z.string().optional(),
  total_area_ha: z.number().positive().optional(),
});

export const farmUpdateSchema = farmCreateSchema.partial();

// ============ Product/Order Schemas ============

export const productSchema = z.object({
  name: z.string().min(2),
  category: z.string(),
  price: z.number().positive(),
  quantity: z.number().nonnegative(),
  unit: z.string(),
});
