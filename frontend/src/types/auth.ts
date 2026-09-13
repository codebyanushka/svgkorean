export type Role = 'ADMIN' | 'TEACHER' | 'STUDENT'

export interface AuthUser {
  id: string
  username: string
  role: Role
}
