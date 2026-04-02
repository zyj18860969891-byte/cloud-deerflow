# Dashboard Deployment Guide

This guide provides comprehensive instructions for deploying and managing the Dashboard functionality in DeerFlow.

## Overview

The Dashboard is a comprehensive monitoring and analytics interface that provides insights into system performance and user activity. It consists of two main components:

- **Admin Dashboard**: System-wide monitoring and management
- **User Dashboard**: Personalized usage statistics and activity tracking

## Prerequisites

### System Requirements

- **Node.js**: >= 22.0.0 (verified with Node 23.11.0)
- **Python**: >= 3.12 (verified with Python 3.12)
- **pnpm**: >= 10.0.0 (verified with pnpm 10.26.2)
- **nginx**: Required for unified local endpoint development

### Dependencies

The Dashboard requires the following main dependencies:

```json
{
  "@tanstack/react-query": "^5.90.17",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "next": "^16.1.7",
  "typescript": "^5.8.2"
}
```

## Development Setup

### 1. Local Development Environment

Start all required services:

```bash
# From the project root directory
make dev
```

This command starts:
- LangGraph backend (port 2024)
- Gateway API (port 8001) 
- Frontend development server (port 3000)
- nginx proxy (port 2026)

Access the Dashboard at: `http://localhost:2026`

### 2. Frontend Development

```bash
cd frontend
pnpm install          # Install dependencies
pnpm dev             # Start development server
pnpm typecheck       # TypeScript validation
pnpm lint            # ESLint validation
pnpm build           # Production build
```

### 3. Backend Integration

The Dashboard integrates with the backend through the following API endpoints:

```typescript
// Admin Dashboard endpoints
GET  /api/admin/dashboard
GET  /api/admin/metrics
GET  /api/admin/system-health

// User Dashboard endpoints  
GET  /api/user/dashboard
GET  /api/user/metrics
GET  /api/user/quota
```

## Production Deployment

### 1. Frontend Build

```bash
cd frontend
$env:BETTER_AUTH_SECRET="your-production-secret" pnpm build
```

### 2. Docker Deployment

```bash
# Build and start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### 3. Environment Configuration

Required environment variables:

```bash
# Better Auth (required for production builds)
BETTER_AUTH_SECRET=your-32-character-secret
BETTER_AUTH_BASE_URL=https://your-domain.com

# Optional: Analytics and monitoring
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-key
```

## Architecture

### Frontend Architecture

```
src/
├── components/
│   ├── dashboard/
│   │   ├── AdminDashboard.tsx     # Admin interface
│   │   ├── UserDashboard.tsx      # User interface  
│   │   └── hooks.ts               # React Query hooks
├── core/
│   └── i18n/                      # Internationalization
│       ├── locales/
│       │   ├── en-US.ts           # English translations
│       │   └── zh-CN.ts           # Chinese translations
│       ├── types.ts               # Translation types
│       └── hooks.ts               # i18n hooks
└── app/
    └── layout.tsx                 # Root layout with providers
```

### Data Flow

1. **React Query**: Manages data fetching, caching, and synchronization
2. **API Gateway**: Routes dashboard requests to appropriate backend services
3. **LangGraph**: Provides agent execution and monitoring data
4. **Database**: Stores metrics, user data, and session information

### Caching Strategy

- **Stale Time**: 30 seconds (data considered fresh)
- **Cache Time**: 5 minutes (data retained in cache)
- **Revalidation**: Automatic on window focus or network reconnect
- **Prefetching**: Optimistic loading for better UX

## Internationalization

### Supported Languages

- **English** (en-US): Primary language
- **Chinese** (zh-CN): Full translation support

### Translation Structure

```typescript
dashboard: {
  title: "Dashboard",
  admin: {
    welcome: "Welcome to Admin Dashboard",
    overview: "System Overview",
    totalUsers: "Total Users",
    // ... more admin translations
  },
  user: {
    welcome: "Welcome to Your Dashboard", 
    overview: "Your Overview",
    cacheHitRate: "Cache Hit Rate",
    // ... more user translations
  }
}
```

### Adding New Languages

1. Add locale to `src/core/i18n/locale.ts`
2. Create translation file in `src/core/i18n/locales/`
3. Update TypeScript types in `src/core/i18n/locales/types.ts`
4. Add language switcher option

## Performance Optimization

### 1. React Query Configuration

```typescript
// Optimal caching configuration
staleTime: 30_000,        // 30 seconds
gcTime: 5 * 60_000,       // 5 minutes
refetchOnWindowFocus: true,
refetchOnReconnect: true
```

### 2. Component Optimization

- **Memoization**: Use `React.memo` for expensive components
- **Virtualization**: Consider for large data lists
- **Lazy Loading**: Dashboard tabs load on demand
- **Image Optimization**: Next.js automatic image optimization

### 3. Bundle Analysis

```bash
# Analyze bundle size
cd frontend
pnpm build --analyze
```

## Monitoring and Observability

### 1. Performance Metrics

- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 2.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1

### 2. Error Tracking

- **Frontend**: React Error Boundary + Sentry integration
- **Backend**: LangGraph tracing + LangSmith integration
- **API**: Gateway error logging and monitoring

### 3. User Analytics

- Dashboard usage statistics
- Performance metric tracking
- Error rate monitoring
- User engagement metrics

## Security Considerations

### 1. Authentication

- Dashboard access requires valid user authentication
- Role-based access control (admin vs user views)
- Session timeout handling

### 2. Data Protection

- API keys and secrets managed via environment variables
- Sensitive data masked in user interfaces
- CORS restrictions for API endpoints

### 3. Input Validation

- TypeScript type checking at compile time
- Runtime validation for API responses
- XSS protection via React's built-in safeguards

## Troubleshooting

### Common Issues

#### 1. Build Failures

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
pnpm install
```

#### 2. TypeScript Errors

```bash
# Check types
pnpm typecheck

# Fix auto-fixable issues
pnpm lint --fix
```

#### 3. API Connection Issues

Verify backend services are running:
```bash
# Check LangGraph
curl http://localhost:2024/health

# Check Gateway API  
curl http://localhost:8001/health
```

### Debug Mode

Enable debug logging:

```bash
# Frontend debug
NEXT_DEBUG=1 pnpm dev

# Backend debug
DEBUG=deerflow:* make dev
```

## Contributing

### Development Workflow

1. Create feature branch from `main`
2. Implement changes with proper TypeScript types
3. Update translations if adding new UI text
4. Test thoroughly in development environment
5. Run validation checks:
   ```bash
   pnpm typecheck
   pnpm lint
   pnpm build
   ```
6. Submit pull request with detailed description

### Code Standards

- **TypeScript**: Strict type checking enabled
- **ESLint**: Standard React/Next.js rules
- **Prettier**: Code formatting consistency
- **Component Structure**: Follow established patterns

## Future Enhancements

### Planned Features

- [ ] Real-time WebSocket updates
- [ ] Advanced filtering and search
- [ ] Export functionality (PDF, CSV)
- [ ] Dark/light theme support
- [ ] Mobile app companion
- [ ] Additional language support
- [ ] Custom dashboard layouts

### Performance Improvements

- [ ] Server-side rendering for dashboard
- [ ] Image lazy loading
- [ ] Code splitting optimization
- [ ] Service worker integration

## Support

For issues and questions:

1. Check the [troubleshooting section](#troubleshooting)
2. Review existing [GitHub issues](https://github.com/bytedance/deer-flow/issues)
3. Create new issue with detailed description
4. Join community discussions

---

*Last Updated: April 2026*  
*Version: DeerFlow 2.0*