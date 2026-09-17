// AA Belt Radar
import type { components } from "@/Api/OpenApi";

// Belt Radar
export type SessionStats = components['schemas']['SessionStatsSchema']
export type Session = components['schemas']['SessionSchema']
export type SessionItem = SessionStats | Session
export type SessionSnapshot = components['schemas']['SnapShotSchema']
export type OreSchema = components['schemas']['OreSchema']
export type MenuSchema = components['schemas']['MenuSchema']
export type BeltTimer = components['schemas']['BeltTimerSchema']
export type Snapshot = components['schemas']['SnapShotSchema']
export type ApexChartSchema = components['schemas']['ApexChartSchema']
export type ApexChartSeriesDataSchema = components['schemas']['ApexChartSeriesDataSchema']
export type ModalSchema = components['schemas']['ModalSchema']
export type ActionSchema = components['schemas']['ActionSchema']
