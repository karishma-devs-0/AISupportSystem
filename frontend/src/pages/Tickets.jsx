import { useState, useEffect } from 'react'
import {
  Box, Typography, Card, CardContent, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Paper, Chip, TextField,
  Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert,
  Accordion, AccordionSummary, AccordionDetails, Slider, Grid
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'
import axios from 'axios'

export default function Tickets() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState('')
  const [minFrustration, setMinFrustration] = useState(0)

  useEffect(() => {
    fetchTickets()
  }, [categoryFilter, sentimentFilter, minFrustration])

  const fetchTickets = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (categoryFilter) params.append('category', categoryFilter)
      if (sentimentFilter) params.append('sentiment', sentimentFilter)
      if (minFrustration > 0) params.append('min_frustration', minFrustration)
      params.append('limit', '50')

      const response = await axios.get(`/api/tickets?${params}`)
      setTickets(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load tickets. Make sure the backend is running.')
      console.error(err)
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

  const categories = [
    'Shipping Delay', 'Product Defect', 'Wrong Item', 'Refund Issue',
    'Account Problem', 'Payment Failed', 'Cancellation Request', 'Other'
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ConfirmationNumberIcon fontSize="large" />
        Ticket Analysis
      </Typography>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Filters</Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  label="Category"
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  {categories.map(cat => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Sentiment</InputLabel>
                <Select
                  value={sentimentFilter}
                  label="Sentiment"
                  onChange={(e) => setSentimentFilter(e.target.value)}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="positive">Positive</MenuItem>
                  <MenuItem value="neutral">Neutral</MenuItem>
                  <MenuItem value="negative">Negative</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Min Frustration: {minFrustration.toFixed(1)}
              </Typography>
              <Slider
                value={minFrustration}
                onChange={(e, val) => setMinFrustration(val)}
                min={0}
                max={1}
                step={0.1}
                size="small"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {!loading && !error && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Showing {tickets.length} tickets
          </Typography>

          {tickets.map((ticket) => (
            <Accordion key={ticket.id}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', pr: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold', minWidth: 120 }}>
                    {ticket.ticket_id}
                  </Typography>
                  <Chip label={ticket.ai_category} color="primary" size="small" />
                  <Chip
                    label={ticket.ai_sentiment}
                    color={getSentimentColor(ticket.ai_sentiment)}
                    size="small"
                  />
                  <Chip
                    label={`Frustration: ${ticket.ai_frustration_score?.toFixed(2)}`}
                    color={getFrustrationColor(ticket.ai_frustration_score)}
                    size="small"
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
                    ${ticket.order_value?.toFixed(2)}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={8}>
                    <Typography variant="subtitle2" color="text.secondary">Customer Message</Typography>
                    <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="body2">{ticket.message}</Typography>
                    </Paper>
                    <Typography variant="subtitle2" color="text.secondary">AI Suggested Response</Typography>
                    <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                      <Typography variant="body2" color="success.contrastText">
                        {ticket.ai_suggested_response}
                      </Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>Details</Typography>
                      <Typography variant="body2">Customer: {ticket.customer_id}</Typography>
                      <Typography variant="body2">Date: {new Date(ticket.timestamp).toLocaleDateString()}</Typography>
                      <Typography variant="body2">Order Value: ${ticket.order_value?.toFixed(2)}</Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </>
      )}
    </Box>
  )
}
