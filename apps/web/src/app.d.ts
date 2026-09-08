declare global {
  namespace App {
    interface Locals { requestId: string; }
    interface Error { message: string; code?: string; requestId?: string; }
  }
}
export {};
