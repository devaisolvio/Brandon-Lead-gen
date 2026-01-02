import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_SERVER_DEV_URL || 'http://localhost:5000'



const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const startPipeline = async (pipelineId) => {
  try {
    const response = await api.post(`/${pipelineId}`)
    return response.data
  } catch (error) {
    if (error.response) {
      // Return the error response data so we can check for 'already_running' status
      if (error.response.status === 409) {
        return error.response.data
      }
      throw new Error(error.response.data.message || 'Failed to start pipeline')
    } else if (error.request) {
      throw new Error('No response from server. Make sure the Flask server is running.')
    } else {
      throw new Error(error.message)
    }
  }
}

export const getPipelineStatus = async (pipelineId) => {
  try {
    const response = await api.get(`/status/${pipelineId}`)
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.message || 'Failed to get pipeline status')
    } else if (error.request) {
      throw new Error('No response from server')
    } else {
      throw new Error(error.message)
    }
  }
}

export const getAllStatuses = async () => {
  try {
    const response = await api.get('/status')
    return response.data
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.message || 'Failed to get statuses')
    } else if (error.request) {
      throw new Error('No response from server')
    } else {
      throw new Error(error.message)
    }
  }
}

export default api

