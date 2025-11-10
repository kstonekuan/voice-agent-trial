import { createEnv } from '@t3-oss/env-core';
import { z } from 'zod';

/**
 * Type-safe environment variable configuration for the client.
 *
 * All client-side environment variables must be prefixed with VITE_
 * to be accessible via import.meta.env in the browser.
 */
export const env = createEnv({
  /**
   * Prefix required for client-side environment variables in Vite.
   */
  clientPrefix: 'VITE_',

  /**
   * Client-side environment variables schema.
   * These are embedded in the client bundle and accessible in the browser.
   */
  client: {
    /**
     * Pipecat runner endpoint URL for starting bot sessions.
     * Defaults to http://localhost:7860 if not specified.
     */
    VITE_RUNNER_ENDPOINT: z.string().default('http://localhost:7860'),
  },

  /**
   * Runtime environment variables provided by Vite.
   * In Vite, use import.meta.env instead of process.env.
   */
  runtimeEnv: import.meta.env,

  /**
   * Treat empty strings as undefined.
   * This is useful for optional variables that might be set to empty strings.
   */
  emptyStringAsUndefined: true,
});
