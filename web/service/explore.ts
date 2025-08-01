import { del, get, patch, post } from './base'
import type { App, AppCategory } from '@/models/explore'
import type { CommonResponse } from '@/models/common'

export const fetchAppList = () => {
  return get<{
    categories: AppCategory[]
    recommended_apps: App[]
  }>('/explore/apps')
}

export const fetchAppDetail = (id: string): Promise<any> => {
  return get(`/explore/apps/${id}`)
}

export const fetchInstalledAppList = (app_id?: string | null) => {
  return get(`/installed-apps${app_id ? `?app_id=${app_id}` : ''}`)
}

export const installApp = (id: string) => {
  return post('/installed-apps', {
    body: {
      app_id: id,
    },
  })
}

export const uninstallApp = (id: string) => {
  return del(`/installed-apps/${id}`)
}

export const updatePinStatus = (id: string, isPinned: boolean) => {
  return patch(`/installed-apps/${id}`, {
    body: {
      is_pinned: isPinned,
    },
  })
}

export const getToolProviders = () => {
  return get('/workspaces/current/tool-providers')
}

// takin code:增加推荐
export const createRecommendedApp = (id: string, description?: string, category?: string) => {
  return post<App>('/explore/apps', { body: { app_id: id, description, category } })
}

// takin code:删除推荐
export const deleteRecommendedApp = (id: string) => {
  return del<CommonResponse>(`/explore/apps/${id}`)
}
