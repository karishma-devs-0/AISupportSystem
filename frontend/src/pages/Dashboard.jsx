import { useState, useEffect } from 'react'
import { Box, Grid, Card, CardContent, Typography, Alert, CircularProgress, Chip } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import WarningIcon from '@mui/icons-material/Warning'
import AttachMoneyIcon from '@mui/icons-material/AttachMoney'
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'
import axios from 'axios'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [mode, setMode] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [statsRes, modeRes] = await Promise.all([
        axios.get('/api/dashboard'),
        axios.get('/api/mode')
      ])
      setStats(statsRes.data)
      setMode(modeRes.data)
      setError(null)
    } catch (err) {
      setError('Failed to load dashboard data. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box sx={{ color: `${color}.main`, fontSize: 40 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard Overview
        </Typography>
        {mode && (
          <Chip 
            label={`${mode.mode.toUpperCase()} MODE - ${mode.provider}`}
            color={mode.mode === 'llm' ? 'success' : 'default'}
            icon={mode.mode === 'llm' ? <TrendingUpIcon /> : null}
          />
        )}
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Tickets"
            value={stats?.total_tickets?.toLocaleString() || 0}
            icon={<ConfirmationNumberIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Avg Frustration"
            value={stats?.avg_frustration || 0}
            icon={<WarningIcon />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Revenue at Risk"
            value={`$${stats?.revenue_at_risk?.toLocaleString() || 0}`}
            icon={<AttachMoneyIcon />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Cost Savings"
            value={`$${stats?.cost_savings?.cost_savings_usd?.toLocaleString() || 0}`}
            icon={<TrendingUpIcon />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Anomalies */}
      {stats?.anomalies && stats.anomalies.length > 0 && (
        <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Anomaly Detected!
          </Typography>
          {stats.anomalies.map((anomaly, idx) => (
            <Typography key={idx} variant="body2">
              <strong>{anomaly.category}</strong>: {anomaly.spike_percentage}% spike 
              ({anomaly.recent_count} vs baseline {anomaly.baseline})
            </Typography>
          ))}
        </Alert>
      )}

      {/* Top Issues Chart */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Top Issues by Category
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats?.top_issues || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#1976d2" name="Ticket Count" />
              <Bar dataKey="revenue_at_risk" fill="#dc004e" name="Revenue at Risk ($)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Top Issues Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Issue Breakdown
          </Typography>
          <Grid container spacing={2}>
            {stats?.top_issues?.map((issue, idx) => (
              <Grid item xs={12} sm={6} md={4} key={idx}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" color="primary">
                      {issue.category}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Count: {issue.count} ({issue.percentage}%)
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Avg Frustration: {issue.avg_frustration}
                    </Typography>
                    <Typography variant="body2" color="error">
                      Revenue at Risk: ${issue.revenue_at_risk.toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Dashboard
