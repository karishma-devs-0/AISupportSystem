import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Typography, TextField, Button, Paper, Chip, CircularProgress, Alert } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import axios from 'axios'

const API_URL = ''

export default function AIAssistant() {
  const [message, setMessage] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [modeInfo, setModeInfo] = useState(null)

  useEffect(() => {
    fetchModeInfo()
  }, [])

  const fetchModeInfo = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/mode`)
      setModeInfo(response.data)
    } catch (err) {
      console.error('Failed to fetch mode info:', err)
    }
  }

  const analyzeMessage = async () => {
    if (!message.trim()) return

    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post(`${API_URL}/api/analyze`, { message })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze message')
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return 'success'
      case 'negative': return 'error'
      default: return 'default'
    }
  }

  const getFrustrationColor = (score) => {
    if (score > 0.7) return 'error'
    if (score > 0.4) return 'warning'
    return 'success'
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SmartToyIcon fontSize="large" />
        AI Assistant
      </Typography>

      {modeInfo && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <strong>{modeInfo.mode.toUpperCase()} MODE</strong> - {modeInfo.provider} | 
          Accuracy: {modeInfo.accuracy} | Cost: {modeInfo.cost}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Test AI Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter a customer message to see real-time AI categorization, sentiment analysis, and response generation.
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="Example: My order hasn't arrived and it's been 2 weeks. This is unacceptable!"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
            onClick={analyzeMessage}
            disabled={loading || !message.trim()}
          >
            Analyze Message
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI Analysis Results
            </Typography>

            <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Category
                </Typography>
                <Chip label={result.category} color="primary" sx={{ mt: 1 }} />
              </Paper>

              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Sentiment
                </Typography>
                <Chip 
                  label={result.sentiment.toUpperCase()} 
                  color={getSentimentColor(result.sentiment)} 
                  sx={{ mt: 1 }} 
                />
              </Paper>

              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Frustration Score
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                  <Chip 
                    label={result.frustration_score.toFixed(2)} 
                    color={getFrustrationColor(result.frustration_score)} 
                  />
                  <Typography variant="body2" color="text.secondary">
                    {result.reasoning}
                  </Typography>
                </Box>
              </Paper>

              <Paper sx={{ p: 2, bgcolor: 'primary.light' }}>
                <Typography variant="subtitle2" color="primary.contrastText">
                  Suggested Response
                </Typography>
                <Typography variant="body1" sx={{ mt: 1, color: 'primary.contrastText' }}>
                  {result.suggested_response}
                </Typography>
              </Paper>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  )
}
