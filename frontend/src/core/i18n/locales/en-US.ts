import {
  CompassIcon,
  GraduationCapIcon,
  ImageIcon,
  MicroscopeIcon,
  PenLineIcon,
  ShapesIcon,
  SparklesIcon,
  VideoIcon,
} from "lucide-react";

import type { Translations } from "./types";

export const enUS: Translations = {
  // Locale meta
  locale: {
    localName: "English",
  },

  // Common
  common: {
    home: "Home",
    settings: "Settings",
    delete: "Delete",
    edit: "Edit",
    rename: "Rename",
    share: "Share",
    openInNewWindow: "Open in new window",
    close: "Close",
    more: "More",
    search: "Search",
    download: "Download",
    thinking: "Thinking",
    artifacts: "Artifacts",
    public: "Public",
    custom: "Custom",
    notAvailableInDemoMode: "Not available in demo mode",
    loading: "Loading...",
    version: "Version",
    lastUpdated: "Last updated",
    code: "Code",
    preview: "Preview",
    cancel: "Cancel",
    save: "Save",
    saving: "Saving",
    creating: "Creating",
    install: "Install",
    create: "Create",
    export: "Export",
    exportAsMarkdown: "Export as Markdown",
    exportAsJSON: "Export as JSON",
    exportSuccess: "Conversation exported",
    yes: "Yes",
    no: "No",
    none: "None",
    error: "Error",
    retry: "Retry",
    actions: "Actions",
    view: "View",
    execute: "Execute",
    showing: "Showing",
    total: "Total",
    previous: "Previous",
    next: "Next",
  },

  // Welcome
  welcome: {
    greeting: "Hello, again!",
    description:
      "Welcome to 🦌 DeerFlow, an open source super agent. With built-in and custom skills, DeerFlow helps you search on the web, analyze data, and generate artifacts like slides, web pages and do almost anything.",

    createYourOwnSkill: "Create Your Own Skill",
    createYourOwnSkillDescription:
      "Create your own skill to release the power of DeerFlow. With customized skills,\nDeerFlow can help you search on the web, analyze data, and generate\n artifacts like slides, web pages and do almost anything.",
  },

  // Clipboard
  clipboard: {
    copyToClipboard: "Copy to clipboard",
    copiedToClipboard: "Copied to clipboard",
    failedToCopyToClipboard: "Failed to copy to clipboard",
    linkCopied: "Link copied to clipboard",
  },

  // Input Box
  inputBox: {
    placeholder: "How can I assist you today?",
    createSkillPrompt:
      "We're going to build a new skill step by step with `skill-creator`. To start, what do you want this skill to do?",
    addAttachments: "Add attachments",
    mode: "Mode",
    flashMode: "Flash",
    flashModeDescription: "Fast and efficient, but may not be accurate",
    reasoningMode: "Reasoning",
    reasoningModeDescription:
      "Reasoning before action, balance between time and accuracy",
    proMode: "Pro",
    proModeDescription:
      "Reasoning, planning and executing, get more accurate results, may take more time",
    ultraMode: "Ultra",
    ultraModeDescription:
      "Pro mode with subagents to divide work; best for complex multi-step tasks",
    reasoningEffort: "Reasoning Effort",
    reasoningEffortMinimal: "Minimal",
    reasoningEffortMinimalDescription: "Retrieval + Direct Output",
    reasoningEffortLow: "Low",
    reasoningEffortLowDescription: "Simple Logic Check + Shallow Deduction",
    reasoningEffortMedium: "Medium",
    reasoningEffortMediumDescription:
      "Multi-layer Logic Analysis + Basic Verification",
    reasoningEffortHigh: "High",
    reasoningEffortHighDescription:
      "Full-dimensional Logic Deduction + Multi-path Verification + Backward Check",
    searchModels: "Search models...",
    surpriseMe: "Surprise",
    surpriseMePrompt: "Surprise me",
    followupLoading: "Generating follow-up questions...",
    followupConfirmTitle: "Send suggestion?",
    followupConfirmDescription:
      "You already have text in the input. Choose how to send it.",
    followupConfirmAppend: "Append & send",
    followupConfirmReplace: "Replace & send",
    suggestions: [
      {
        suggestion: "Write",
        prompt: "Write a blog post about the latest trends on [topic]",
        icon: PenLineIcon,
      },
      {
        suggestion: "Research",
        prompt:
          "Conduct a deep dive research on [topic], and summarize the findings.",
        icon: MicroscopeIcon,
      },
      {
        suggestion: "Collect",
        prompt: "Collect data from [source] and create a report.",
        icon: ShapesIcon,
      },
      {
        suggestion: "Learn",
        prompt: "Learn about [topic] and create a tutorial.",
        icon: GraduationCapIcon,
      },
    ],
    suggestionsCreate: [
      {
        suggestion: "Webpage",
        prompt: "Create a webpage about [topic]",
        icon: CompassIcon,
      },
      {
        suggestion: "Image",
        prompt: "Create an image about [topic]",
        icon: ImageIcon,
      },
      {
        suggestion: "Video",
        prompt: "Create a video about [topic]",
        icon: VideoIcon,
      },
      {
        type: "separator",
      },
      {
        suggestion: "Skill",
        prompt:
          "We're going to build a new skill step by step with `skill-creator`. To start, what do you want this skill to do?",
        icon: SparklesIcon,
      },
    ],
  },

  // Sidebar
  sidebar: {
    newChat: "New chat",
    chats: "Chats",
    recentChats: "Recent chats",
    demoChats: "Demo chats",
    agents: "Agents",
    tools: "Tools",
  },

  // Agents
  agents: {
    title: "Agents",
    description:
      "Create and manage custom agents with specialized prompts and capabilities.",
    newAgent: "New Agent",
    emptyTitle: "No custom agents yet",
    emptyDescription:
      "Create your first custom agent with a specialized system prompt.",
    chat: "Chat",
    delete: "Delete",
    deleteConfirm:
      "Are you sure you want to delete this agent? This action cannot be undone.",
    deleteSuccess: "Agent deleted",
    newChat: "New chat",
    createPageTitle: "Design your Agent",
    createPageSubtitle:
      "Describe the agent you want — I'll help you create it through conversation.",
    nameStepTitle: "Name your new Agent",
    nameStepHint:
      "Letters, digits, and hyphens only — stored lowercase (e.g. code-reviewer)",
    nameStepPlaceholder: "e.g. code-reviewer",
    nameStepContinue: "Continue",
    nameStepInvalidError:
      "Invalid name — use only letters, digits, and hyphens",
    nameStepAlreadyExistsError: "An agent with this name already exists",
    nameStepCheckError: "Could not verify name availability — please try again",
    nameStepBootstrapMessage:
      "The new custom agent name is {name}. Let's bootstrap it's **SOUL**.",
    agentCreated: "Agent created!",
    startChatting: "Start chatting",
    backToGallery: "Back to Gallery",
  },

  // Breadcrumb
  breadcrumb: {
    workspace: "Workspace",
    chats: "Chats",
  },

  // Workspace
  workspace: {
    officialWebsite: "DeerFlow's official website",
    githubTooltip: "DeerFlow on Github",
    settingsAndMore: "Settings and more",
    visitGithub: "DeerFlow on GitHub",
    reportIssue: "Report a issue",
    contactUs: "Contact us",
    about: "About DeerFlow",
  },

  // Conversation
  conversation: {
    noMessages: "No messages yet",
    startConversation: "Start a conversation to see messages here",
  },

  // Chats
  chats: {
    searchChats: "Search chats",
  },

  // Page titles (document title)
  pages: {
    appName: "DeerFlow",
    chats: "Chats",
    newChat: "New chat",
    untitled: "Untitled",
  },

  // Tool calls
  toolCalls: {
    moreSteps: (count: number) => `${count} more step${count === 1 ? "" : "s"}`,
    lessSteps: "Less steps",
    executeCommand: "Execute command",
    presentFiles: "Present files",
    needYourHelp: "Need your help",
    useTool: (toolName: string) => `Use "${toolName}" tool`,
    searchFor: (query: string) => `Search for "${query}"`,
    searchForRelatedInfo: "Search for related information",
    searchForRelatedImages: "Search for related images",
    searchForRelatedImagesFor: (query: string) =>
      `Search for related images for "${query}"`,
    searchOnWebFor: (query: string) => `Search on the web for "${query}"`,
    viewWebPage: "View web page",
    listFolder: "List folder",
    readFile: "Read file",
    writeFile: "Write file",
    clickToViewContent: "Click to view file content",
    writeTodos: "Update to-do list",
    skillInstallTooltip: "Install skill and make it available to DeerFlow",
  },

  // Subtasks
  uploads: {
    uploading: "Uploading...",
    uploadingFiles: "Uploading files, please wait...",
  },

  subtasks: {
    subtask: "Subtask",
    executing: (count: number) =>
      `Executing ${count === 1 ? "" : count + " "}subtask${count === 1 ? "" : "s in parallel"}`,
    in_progress: "Running subtask",
    completed: "Subtask completed",
    failed: "Subtask failed",
  },

  // Token Usage
  tokenUsage: {
    title: "Token Usage",
    input: "Input",
    output: "Output",
    total: "Total",
  },

  // Shortcuts
  shortcuts: {
    searchActions: "Search actions...",
    noResults: "No results found.",
    actions: "Actions",
    keyboardShortcuts: "Keyboard Shortcuts",
    keyboardShortcutsDescription:
      "Navigate DeerFlow faster with keyboard shortcuts.",
    openCommandPalette: "Open Command Palette",
    toggleSidebar: "Toggle Sidebar",
  },

  // Tools
  tools: {
    title: "Tools",
    description: "Manage the configuration and enabled status of MCP tools.",
    // Tool Management Panel
    toolList: "Tool List",
    createTool: "Create Tool",
    createToolDescription: "Create a new custom tool",
    editTool: "Edit Tool",
    editToolDescription: "Modify tool configuration",
    toolDetails: "Tool Details",
    toolDetailsDescription: "View detailed information about this tool",
    executeTool: "Execute Tool",
    executeToolDescription: "Execute this tool with custom parameters",
    executing: "Executing...",
    executionSuccess: "Execution completed successfully",
    executionFailed: "Execution failed",
    inputParameters: "Input Parameters",
    inputParametersHint: "Enter JSON parameters for the tool execution",
    expectedParameters: "Expected parameters",
    searchPlaceholder: "Search tools...",
    noToolsFound: "No tools found",
    name: "Name",
    type: "Type",
    category: "Category",
    status: "Status",
    executions: "Executions",
    successRate: "Success Rate",
    actions: "Actions",
    view: "View",
    enabled: "Enabled",
    disabled: "Disabled",
    totalExecutions: "Total",
    successfulExecutions: "Success",
    failedExecutions: "Failed",
    avgExecutionTime: "Avg. Time",
    lastExecutedAt: "Last Executed",
    modulePath: "Module Path",
    className: "Class Name",
    argsSchema: "Arguments Schema",
    requiredRoles: "Required Roles",
    version: "Version",
    versionNotes: "Version Notes",
    tenantScoped: "Tenant Scoped",
    isBuiltin: "Built-in",
    isSystem: "System",
    createdFromConfig: "Created From Config",
    createdAt: "Created At",
    updatedAt: "Updated At",
    confirmDeleteTitle: "Delete Tool",
    confirmDeleteDescription: "Are you sure you want to delete the tool '{name}'? This action cannot be undone.",
    tags: "Tags",
    statistics: "Statistics",
    none: "None",
    // Tool types
    types: {
      custom: "Custom",
      mcp: "MCP",
      builtin: "Built-in",
      agent: "Agent",
    },
    invalidJSONFormat: "Invalid JSON format",
  },

  // Settings
  settings: {
    title: "Settings",
    description: "Adjust how DeerFlow looks and behaves for you.",
    sections: {
      appearance: "Appearance",
      memory: "Memory",
      tools: "Tools",
      skills: "Skills",
      notification: "Notification",
      about: "About",
    },
    memory: {
      title: "Memory",
      description:
        "DeerFlow automatically learns from your conversations in the background. These memories help DeerFlow understand you better and deliver a more personalized experience.",
      empty: "No memory data to display.",
      rawJson: "Raw JSON",
      addFact: "Add fact",
      addFactTitle: "Add memory fact",
      editFactTitle: "Edit memory fact",
      addFactSuccess: "Fact created",
      editFactSuccess: "Fact updated",
      clearAll: "Clear all memory",
      clearAllConfirmTitle: "Clear all memory?",
      clearAllConfirmDescription:
        "This will remove all saved summaries and facts. This action cannot be undone.",
      clearAllSuccess: "All memory cleared",
      factDeleteConfirmTitle: "Delete this fact?",
      factDeleteConfirmDescription:
        "This fact will be removed from memory immediately. This action cannot be undone.",
      factDeleteSuccess: "Fact deleted",
      factContentLabel: "Content",
      factCategoryLabel: "Category",
      factConfidenceLabel: "Confidence",
      factContentPlaceholder: "Describe the memory fact you want to save",
      factCategoryPlaceholder: "context",
      factConfidenceHint: "Use a number between 0 and 1.",
      factSave: "Save fact",
      factValidationContent: "Fact content cannot be empty.",
      factValidationConfidence: "Confidence must be a number between 0 and 1.",
      manualFactSource: "Manual",
      noFacts: "No saved facts yet.",
      summaryReadOnly:
        "Summary sections are read-only for now. You can currently add, edit, or delete individual facts, or clear all memory.",
      memoryFullyEmpty: "No memory saved yet.",
      factPreviewLabel: "Fact to delete",
      searchPlaceholder: "Search memory",
      filterAll: "All",
      filterFacts: "Facts",
      filterSummaries: "Summaries",
      noMatches: "No matching memory found.",
      markdown: {
        overview: "Overview",
        userContext: "User context",
        work: "Work",
        personal: "Personal",
        topOfMind: "Top of mind",
        historyBackground: "History",
        recentMonths: "Recent months",
        earlierContext: "Earlier context",
        longTermBackground: "Long-term background",
        updatedAt: "Updated at",
        facts: "Facts",
        empty: "(empty)",
        table: {
          category: "Category",
          confidence: "Confidence",
          confidenceLevel: {
            veryHigh: "Very high",
            high: "High",
            normal: "Normal",
            unknown: "Unknown",
          },
          content: "Content",
          source: "Source",
          createdAt: "CreatedAt",
          view: "View",
        },
      },
    },
    appearance: {
      themeTitle: "Theme",
      themeDescription:
        "Choose how the interface follows your device or stays fixed.",
      system: "System",
      light: "Light",
      dark: "Dark",
      systemDescription: "Match the operating system preference automatically.",
      lightDescription: "Bright palette with higher contrast for daytime.",
      darkDescription: "Dim palette that reduces glare for focus.",
      languageTitle: "Language",
      languageDescription: "Switch between languages.",
    },
    skills: {
      title: "Agent Skills",
      description:
        "Manage the configuration and enabled status of the agent skills.",
      createSkill: "Create skill",
      emptyTitle: "No agent skill yet",
      emptyDescription:
        "Put your agent skill folders under the `/skills/custom` folder under the root folder of DeerFlow.",
      emptyButton: "Create Your First Skill",
    },
    notification: {
      title: "Notification",
      description:
        "DeerFlow only sends a completion notification when the window is not active. This is especially useful for long-running tasks so you can switch to other work and get notified when done.",
      requestPermission: "Request notification permission",
      deniedHint:
        "Notification permission was denied. You can enable it in your browser's site settings to receive completion alerts.",
      testButton: "Send test notification",
      testTitle: "DeerFlow",
      testBody: "This is a test notification.",
      notSupported: "Your browser does not support notifications.",
      disableNotification: "Disable notification",
    },
    acknowledge: {
      emptyTitle: "Acknowledgements",
      emptyDescription: "Credits and acknowledgements will show here.",
    },
    // Dashboard
    dashboard: {
      title: "Dashboard",
      description: "Monitor your usage and system performance",
      // Admin Dashboard
      admin: {
        title: "Admin Dashboard",
        description: "System overview and user management",
        userManagement: "User Management",
        systemHealth: "System Health",
        performance: "Performance",
        security: "Security",
        totalUsers: "Total Users",
        activeUsers: "Active Users",
        apiCalls: "API Calls (Today)",
        errorRate: "Error Rate",
        costAnalysis: "Cost Analysis",
        welcome: "Welcome to Admin Dashboard",
        overview: "System Overview",
        activeSessions: "Active Sessions",
        totalAgents: "Total Agents",
        systemLoad: "System Load",
        memoryUsage: "Memory Usage",
        cpuUsage: "CPU Usage",
        uptime: "Uptime",
        recentActivity: "Recent Activity",
        noActivity: "No recent activity",
        loading: "Loading dashboard data...",
        error: "Failed to load dashboard data",
      },
      // User Dashboard
      user: {
        title: "My Dashboard",
        description: "Your usage statistics and activity",
        myUsage: "My Usage",
        toolExecutions: "Tool Executions",
        cacheHitRate: "Cache Hit Rate",
        recentActivity: "Recent Activity",
        storageUsed: "Storage Used",
        apiQuota: "API Quota",
        remainingQuota: "Remaining Quota",
        successRate: "Success Rate",
        apiUsage: "API Usage",
        topTools: "Top Tools",
        welcome: "Welcome to Your Dashboard",
        overview: "Your Overview",
        quotaRemaining: "Quota Remaining",
        toolsUsed: "Tools Used",
        recentSessions: "Recent Sessions",
        noSessions: "No recent sessions",
        loading: "Loading your dashboard...",
        error: "Failed to load your dashboard",
      },
      // Common
      common: {
        lastUpdated: "Last updated",
        refresh: "Refresh",
        loading: "Loading...",
        error: "Error loading data",
        noData: "No data available",
        viewDetails: "View Details",
        exportData: "Export Data",
        yes: "Yes",
        no: "No",
        never: "Never",
        retry: "Retry",
        back: "Back",
        close: "Close",
        save: "Save",
        cancel: "Cancel",
        confirm: "Confirm",
        ok: "OK",
      },
      // Database Optimization
      databaseOptimization: {
        title: "Database Optimization",
        description: "Monitor and optimize database performance",
        tabs: {
          overview: "Overview",
          queryAnalysis: "Query Analysis",
          indexManagement: "Index Management",
          connectionPool: "Connection Pool",
        },
        metrics: {
          queryTime: "Avg Query Time",
          avgQueryTime: "Average query execution time",
          qps: "Queries/sec",
          queriesPerSecond: "Queries per second",
          cacheHitRatio: "Cache Hit Ratio",
          cacheEfficiency: "Database cache efficiency",
          slowQueries: "Slow Queries",
          slowQueriesCount: "Number of slow queries detected",
        },
        charts: {
          performanceTrend: "Performance Trend",
          performanceTrendDesc: "Query time and throughput over time",
          tableSizeDistribution: "Table Size Distribution",
          tableSizeDistributionDesc: "Distribution of table sizes",
        },
        recommendations: {
          title: "Optimization Recommendations",
          description: "AI-powered suggestions for database improvements",
          improvement: "Improvement",
          implementationCost: "Implementation Cost",
          riskLevel: "Risk Level",
        },
        queryAnalysis: {
          title: "Query Performance Analysis",
          description: "Analyze SQL queries for performance issues",
          placeholder: "Enter SQL query to analyze...",
          analyze: "Analyze",
          getPlan: "Get Execution Plan",
          executionTime: "Execution Time",
          rowsExamined: "Rows Examined",
          rowsReturned: "Rows Returned",
          suggestions: "Suggestions",
          indexUsage: "Index Usage",
          indexName: "Index Name",
          used: "Used",
          efficiency: "Efficiency",
          queryPlan: "Query Execution Plan",
        },
        slowQueries: {
          title: "Slow Queries",
          description: "Queries exceeding {threshold}s execution time",
          query: "Query",
          executionTime: "Time",
          database: "Database",
          user: "User",
          timestamp: "Time",
        },
        indexManagement: {
          title: "Index Management",
          description: "Manage database indexes for optimal performance",
          suggestions: "Index Suggestions",
          suggestionsDesc: "Recommended indexes to improve query performance",
          noSuggestions: "No index suggestions available",
          createIndex: "Create Index",
          indexName: "Index Name",
          indexType: "Index Type",
          improvement: "Expected Improvement",
          usageReport: "Index Usage Report",
          usageReportDesc: "Analysis of current index usage patterns",
          unusedIndexes: "Unused Indexes",
          noUnusedIndexes: "No unused indexes found",
          frequentlyUsed: "Frequently Used Indexes",
          usageCount: "Usage Count",
          cleanupUnused: "Cleanup Unused Indexes",
          drop: "Drop",
          size: "Size",
          lastUsed: "Last Used",
          actions: "Actions",
        },
        tableStats: {
          title: "Table Statistics",
          description: "Detailed statistics for all database tables",
          tableName: "Table",
          rowCount: "Rows",
          size: "Size",
          indexCount: "Indexes",
          fragmentation: "Fragmentation",
          growthRate: "Growth Rate",
          lastAnalyzed: "Last Analyzed",
        },
        poolMetrics: {
          title: "Connection Pool Metrics",
          details: "Connection Pool Details",
          poolSize: "Pool Size",
          totalConnections: "Total connections in pool",
          checkedOut: "Checked Out",
          activeConnections: "Active connections in use",
          idle: "Idle",
          idleConnections: "Idle connections available",
          overflow: "Overflow",
          overflowConnections: "Overflow connections created",
          maxOverflow: "Max Overflow",
          poolTimeout: "Pool Timeout",
          recycle: "Recycle",
          invalidated: "Invalidated",
          checkedIn: "Checked In",
          utilization: "Utilization",
        },
      },
    },

    
  },
};
