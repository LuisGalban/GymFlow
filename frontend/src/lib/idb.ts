"use client"

import { openDB, DBSchema, IDBPDatabase } from "idb"

interface GymFlowDB extends DBSchema {
  pendingCheckins: {
    key: number
    value: {
      miembro_id: number
      timestamp: string
    }
    indexes: { "by-timestamp": string }
  }
}

let dbPromise: Promise<IDBPDatabase<GymFlowDB>> | null = null

function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<GymFlowDB>('gymflow-db', 1, {
      upgrade(db) {
        const store = db.createObjectStore('pendingCheckins', { keyPath: 'id', autoIncrement: true })
        store.createIndex('by-timestamp', 'timestamp')
      },
    })
  }
  return dbPromise
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
