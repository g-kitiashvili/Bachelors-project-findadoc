import { env } from "$env/dynamic/private";

export const API_BASE = env.API_URL ?? "http://localhost:8080";
