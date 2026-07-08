"use client"

import { openDB, DBSchema, IDBPDatabase } from "idb"

export interface MemberCacheEntry {
  id: number
  cedula: string
  nombre: string
  telefono: string | null
  estatus_actual: string | null
}

interface GymFlowDB extends DBSchema {
  pendingCheckins: {
    key: number
    value: {
      miembro_id: number
      timestamp: string
    }
    indexes: { "by-timestamp": string }
  }
  membersCache: {
    key: number
    value: MemberCacheEntry
  }
}

let dbPromise: Promise<IDBPDatabase<GymFlowDB>> | null = null

function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<GymFlowDB>('gymflow-db', 2, {
      upgrade(db, oldVersion) {
        if (oldVersion < 1) {
          const store = db.createObjectStore('pendingCheckins', { keyPath: 'id', autoIncrement: true })
          store.createIndex('by-timestamp', 'timestamp')
        }
        if (oldVersion < 2) {
          db.createObjectStore('membersCache', { keyPath: 'id' })
        }
      },
    })
  }
  return dbPromise
}

export async function cacheMembers(members: MemberCacheEntry[]): Promise<void> {
  const db = await getDB()
  const tx = db.transaction('membersCache', 'readwrite')
  await Promise.all([
    tx.objectStore('membersCache').clear(),
    ...members.map((m) => tx.objectStore('membersCache').put(m)),
    tx.done,
  ])
}

export async function searchMemberOffline(cedula: string): Promise<MemberCacheEntry | undefined> {
  const db = await getDB()
  const all = await db.getAll('membersCache')
  return all.find((m) => m.cedula === cedula)
}

export async function addPendingCheckin(miembro_id: number) {
  const db = await getDB()
  await db.add('pendingCheckins', { miembro_id, timestamp: new Date().toISOString() })
}

export async function getAllPendingCheckins() {
  const db = await getDB()
  return db.getAll('pendingCheckins')
}

export async function clearPendingCheckins() {
  const db = await getDB()
  const all = await db.getAllKeys('pendingCheckins')
  await Promise.all(all.map((key) => db.delete('pendingCheckins', key)))
}
