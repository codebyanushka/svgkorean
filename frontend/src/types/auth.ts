export type Role = 'TEACHER' | 'STUDENT'

export interface AuthUser {
  id: string
  username: string
  role: Role
}
