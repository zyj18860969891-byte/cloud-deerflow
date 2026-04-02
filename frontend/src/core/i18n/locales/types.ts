import type { LucideIcon } from "lucide-react";

export interface Translations {
  // Locale meta
  locale: {
    localName: string;
  };

  // Common
  common: {
    home: string;
    settings: string;
    delete: string;
    edit: string;
    rename: string;
    share: string;
    openInNewWindow: string;
    close: string;
    more: string;
    search: string;
    download: string;
    thinking: string;
    artifacts: string;
    public: string;
    custom: string;
    notAvailableInDemoMode: string;
    loading: string;
    version: string;
    lastUpdated: string;
    code: string;
    preview: string;
    cancel: string;
    save: string;
    saving: string;
    creating: string;
    install: string;
    create: string;
    export: string;
    exportAsMarkdown: string;
    exportAsJSON: string;
    exportSuccess: string;
    yes: string;
    no: string;
    none: string;
    error: string;
    retry: string;
    actions: string;
    view: string;
    execute: string;
    showing: string;
    total: string;
    previous: string;
    next: string;
  };

  // Welcome
  welcome: {
    greeting: string;
    description: string;
    createYourOwnSkill: string;
    createYourOwnSkillDescription: string;
  };

  // Clipboard
  clipboard: {
    copyToClipboard: string;
    copiedToClipboard: string;
    failedToCopyToClipboard: string;
    linkCopied: string;
  };

  // Input Box
  inputBox: {
    placeholder: string;
    createSkillPrompt: string;
    addAttachments: string;
    mode: string;
    flashMode: string;
    flashModeDescription: string;
    reasoningMode: string;
    reasoningModeDescription: string;
    proMode: string;
    proModeDescription: string;
    ultraMode: string;
    ultraModeDescription: string;
    reasoningEffort: string;
    reasoningEffortMinimal: string;
    reasoningEffortMinimalDescription: string;
    reasoningEffortLow: string;
    reasoningEffortLowDescription: string;
    reasoningEffortMedium: string;
    reasoningEffortMediumDescription: string;
    reasoningEffortHigh: string;
    reasoningEffortHighDescription: string;
    searchModels: string;
    surpriseMe: string;
    surpriseMePrompt: string;
    followupLoading: string;
    followupConfirmTitle: string;
    followupConfirmDescription: string;
    followupConfirmAppend: string;
    followupConfirmReplace: string;
    suggestions: {
      suggestion: string;
      prompt: string;
      icon: LucideIcon;
    }[];
    suggestionsCreate: (
      | {
          suggestion: string;
          prompt: string;
          icon: LucideIcon;
        }
      | {
          type: "separator";
        }
    )[];
  };

  // Sidebar
  sidebar: {
    recentChats: string;
    newChat: string;
    chats: string;
    demoChats: string;
    agents: string;
    tools: string;
  };

  // Agents
  agents: {
    title: string;
    description: string;
    newAgent: string;
    emptyTitle: string;
    emptyDescription: string;
    chat: string;
    delete: string;
    deleteConfirm: string;
    deleteSuccess: string;
    newChat: string;
    createPageTitle: string;
    createPageSubtitle: string;
    nameStepTitle: string;
    nameStepHint: string;
    nameStepPlaceholder: string;
    nameStepContinue: string;
    nameStepInvalidError: string;
    nameStepAlreadyExistsError: string;
    nameStepCheckError: string;
    nameStepBootstrapMessage: string;
    agentCreated: string;
    startChatting: string;
    backToGallery: string;
  };

  // Breadcrumb
  breadcrumb: {
    workspace: string;
    chats: string;
  };

  // Workspace
  workspace: {
    officialWebsite: string;
    githubTooltip: string;
    settingsAndMore: string;
    visitGithub: string;
    reportIssue: string;
    contactUs: string;
    about: string;
  };

  // Conversation
  conversation: {
    noMessages: string;
    startConversation: string;
  };

  // Chats
  chats: {
    searchChats: string;
  };

  // Page titles (document title)
  pages: {
    appName: string;
    chats: string;
    newChat: string;
    untitled: string;
  };

  // Tool calls
  toolCalls: {
    moreSteps: (count: number) => string;
    lessSteps: string;
    executeCommand: string;
    presentFiles: string;
    needYourHelp: string;
    useTool: (toolName: string) => string;
    searchForRelatedInfo: string;
    searchForRelatedImages: string;
    searchFor: (query: string) => string;
    searchForRelatedImagesFor: (query: string) => string;
    searchOnWebFor: (query: string) => string;
    viewWebPage: string;
    listFolder: string;
    readFile: string;
    writeFile: string;
    clickToViewContent: string;
    writeTodos: string;
    skillInstallTooltip: string;
  };

  // Uploads
  uploads: {
    uploading: string;
    uploadingFiles: string;
  };

  // Subtasks
  subtasks: {
    subtask: string;
    executing: (count: number) => string;
    in_progress: string;
    completed: string;
    failed: string;
  };

  // Token Usage
  tokenUsage: {
    title: string;
    input: string;
    output: string;
    total: string;
  };

  // Shortcuts
  shortcuts: {
    searchActions: string;
    noResults: string;
    actions: string;
    keyboardShortcuts: string;
    keyboardShortcutsDescription: string;
    openCommandPalette: string;
    toggleSidebar: string;
  };

  // Tools
  tools: {
    title: string;
    description: string;
    // Tool Management Panel
    toolList: string;
    createTool: string;
    createToolDescription: string;
    editTool: string;
    editToolDescription: string;
    toolDetails: string;
    toolDetailsDescription: string;
    executeTool: string;
    executeToolDescription: string;
    executing: string;
    executionSuccess: string;
    executionFailed: string;
    inputParameters: string;
    inputParametersHint: string;
    expectedParameters: string;
    searchPlaceholder: string;
    noToolsFound: string;
    name: string;
    type: string;
    category: string;
    status: string;
    executions: string;
    successRate: string;
    actions: string;
    view: string;
    enabled: string;
    disabled: string;
    totalExecutions: string;
    successfulExecutions: string;
    failedExecutions: string;
    avgExecutionTime: string;
    lastExecutedAt: string;
    modulePath: string;
    className: string;
    argsSchema: string;
    requiredRoles: string;
    version: string;
    versionNotes: string;
    tenantScoped: string;
    isBuiltin: string;
    isSystem: string;
    createdFromConfig: string;
    createdAt: string;
    updatedAt: string;
    confirmDeleteTitle: string;
    confirmDeleteDescription: string;
    tags: string;
    statistics: string;
    none: string;
    // Tool types
    types: {
      custom: string;
      mcp: string;
      builtin: string;
      agent: string;
    };
    invalidJSONFormat: string;
  };

  // Settings
  settings: {
    title: string;
    description: string;
    sections: {
      appearance: string;
      memory: string;
      tools: string;
      skills: string;
      notification: string;
      about: string;
    };
    memory: {
      title: string;
      description: string;
      empty: string;
      rawJson: string;
      addFact: string;
      addFactTitle: string;
      editFactTitle: string;
      addFactSuccess: string;
      editFactSuccess: string;
      clearAll: string;
      clearAllConfirmTitle: string;
      clearAllConfirmDescription: string;
      clearAllSuccess: string;
      factDeleteConfirmTitle: string;
      factDeleteConfirmDescription: string;
      factDeleteSuccess: string;
      factContentLabel: string;
      factCategoryLabel: string;
      factConfidenceLabel: string;
      factContentPlaceholder: string;
      factCategoryPlaceholder: string;
      factConfidenceHint: string;
      factSave: string;
      factValidationContent: string;
      factValidationConfidence: string;
      manualFactSource: string;
      noFacts: string;
      summaryReadOnly: string;
      memoryFullyEmpty: string;
      factPreviewLabel: string;
      searchPlaceholder: string;
      filterAll: string;
      filterFacts: string;
      filterSummaries: string;
      noMatches: string;
      markdown: {
        overview: string;
        userContext: string;
        work: string;
        personal: string;
        topOfMind: string;
        historyBackground: string;
        recentMonths: string;
        earlierContext: string;
        longTermBackground: string;
        updatedAt: string;
        facts: string;
        empty: string;
        table: {
          category: string;
          confidence: string;
          confidenceLevel: {
            veryHigh: string;
            high: string;
            normal: string;
            unknown: string;
          };
          content: string;
          source: string;
          createdAt: string;
          view: string;
        };
      };
    };
    appearance: {
      themeTitle: string;
      themeDescription: string;
      system: string;
      light: string;
      dark: string;
      systemDescription: string;
      lightDescription: string;
      darkDescription: string;
      languageTitle: string;
      languageDescription: string;
    };
    skills: {
      title: string;
      description: string;
      createSkill: string;
      emptyTitle: string;
      emptyDescription: string;
      emptyButton: string;
    };
    notification: {
      title: string;
      description: string;
      requestPermission: string;
      deniedHint: string;
      testButton: string;
      testTitle: string;
      testBody: string;
      notSupported: string;
      disableNotification: string;
    };
    acknowledge: {
      emptyTitle: string;
      emptyDescription: string;
    };
    // Dashboard
    dashboard: {
      title: string;
      description: string;
      // Admin Dashboard
      admin: {
        title: string;
        description: string;
        userManagement: string;
        systemHealth: string;
        performance: string;
        security: string;
        totalUsers: string;
        activeUsers: string;
        apiCalls: string;
        errorRate: string;
        costAnalysis: string;
        welcome: string;
        overview: string;
        activeSessions: string;
        totalAgents: string;
        systemLoad: string;
        memoryUsage: string;
        cpuUsage: string;
        uptime: string;
        recentActivity: string;
        noActivity: string;
        loading: string;
        error: string;
      };
      // User Dashboard
      user: {
        title: string;
        description: string;
        myUsage: string;
        toolExecutions: string;
        cacheHitRate: string;
        recentActivity: string;
        storageUsed: string;
        apiQuota: string;
        remainingQuota: string;
        successRate: string;
        apiUsage: string;
        topTools: string;
        welcome: string;
        overview: string;
        quotaRemaining: string;
        toolsUsed: string;
        recentSessions: string;
        noSessions: string;
        loading: string;
        error: string;
      };
      // Common
      common: {
        lastUpdated: string;
        refresh: string;
        loading: string;
        error: string;
        noData: string;
        viewDetails: string;
        exportData: string;
        yes: string;
        no: string;
        never: string;
        retry: string;
        back: string;
        close: string;
        save: string;
        cancel: string;
        confirm: string;
        ok: string;
      };
      // Database Optimization
      databaseOptimization: {
        title: string;
        description: string;
        tabs: {
          overview: string;
          queryAnalysis: string;
          indexManagement: string;
          connectionPool: string;
        };
        metrics: {
          queryTime: string;
          avgQueryTime: string;
          qps: string;
          queriesPerSecond: string;
          cacheHitRatio: string;
          cacheEfficiency: string;
          slowQueries: string;
          slowQueriesCount: string;
        };
        charts: {
          performanceTrend: string;
          performanceTrendDesc: string;
          tableSizeDistribution: string;
          tableSizeDistributionDesc: string;
        };
        recommendations: {
          title: string;
          description: string;
          improvement: string;
          implementationCost: string;
          riskLevel: string;
        };
        queryAnalysis: {
          title: string;
          description: string;
          placeholder: string;
          analyze: string;
          getPlan: string;
          executionTime: string;
          rowsExamined: string;
          rowsReturned: string;
          suggestions: string;
          indexUsage: string;
          indexName: string;
          used: string;
          efficiency: string;
          queryPlan: string;
        };
        slowQueries: {
          title: string;
          description: string;
          query: string;
          executionTime: string;
          database: string;
          user: string;
          timestamp: string;
        };
        indexManagement: {
          title: string;
          description: string;
          suggestions: string;
          suggestionsDesc: string;
          noSuggestions: string;
          createIndex: string;
          indexName: string;
          indexType: string;
          improvement: string;
          usageReport: string;
          usageReportDesc: string;
          unusedIndexes: string;
          noUnusedIndexes: string;
          frequentlyUsed: string;
          usageCount: string;
          cleanupUnused: string;
          drop: string;
          size: string;
          lastUsed: string;
          actions: string;
        };
        tableStats: {
          title: string;
          description: string;
          tableName: string;
          rowCount: string;
          size: string;
          indexCount: string;
          fragmentation: string;
          growthRate: string;
          lastAnalyzed: string;
        };
        poolMetrics: {
          title: string;
          details: string;
          poolSize: string;
          totalConnections: string;
          checkedOut: string;
          activeConnections: string;
          idle: string;
          idleConnections: string;
          overflow: string;
          overflowConnections: string;
          maxOverflow: string;
          poolTimeout: string;
          recycle: string;
          invalidated: string;
          checkedIn: string;
          utilization: string;
        };
      };
    };

    
  };
}
