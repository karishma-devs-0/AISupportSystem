import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Typography, Grid, Paper, CircularProgress } from '@mui/material'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import axios from 'axios'

const API_URL = ''

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658']

export default function Analytics() {
  const [stats, setStats] = useState(null)
  const [trends, setTrends] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [statsRes, trendsRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard`),
        axios.get(`${API_URL}/api/trends`)
      ])
      setStats(statsRes.data)
      setTrends(trendsRes.data)
    } catch (err) {
      console.error('Failed to fetch analytics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  const categoryData = stats?.category_distribution 
    ? Object.entries(stats.category_distribution).map(([name, value]) => ({ name, value }))
    : []

  const sentimentData = stats?.sentiment_distribution
    ? Object.entries(stats.sentiment_distribution).map(([name, value]) => ({ name, value }))
    : []

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <TrendingUpIcon fontSize="large" />
        Analytics & Insights
      </Typography>

      <Grid container spacing={3}>
        {/* Cost Savings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cost Savings Analysis
              </Typography>
              {stats?.cost_savings && (
                <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
                  <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
                    <Typography variant="body2" color="success.contrastText">
                      Monthly Savings
                    </Typography>
                    <Typography variant="h4" color="success.contrastText">
                      ${stats.cost_savings.cost_savings_usd.toLocaleString()}
                    </Typography>
                  </Paper>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Automatable Tickets
                    </Typography>
                    <Typography variant="h5">
                      {stats.cost_savings.automatable_tickets.toLocaleString()} ({stats.cost_savings.efficiency_gain})
                    </Typography>
                  </Paper>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Hours Saved
                    </Typography>
                    <Typography variant="h5">
                      {stats.cost_savings.hours_saved.toLocaleString()} hours
                    </Typography>
                  </Paper>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Category Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Category Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Sentiment Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sentiment Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Daily Trends */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Daily Ticket Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends?.daily_trends || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#8884d8" name="Tickets" />
                  <Line type="monotone" dataKey="avg_frustration" stroke="#82ca9d" name="Avg Frustration" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Issues */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Issues by Revenue Impact
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats?.top_issues || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="revenue_at_risk" fill="#FF8042" name="Revenue at Risk ($)" />
                  <Bar dataKey="count" fill="#0088FE" name="Ticket Count" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
