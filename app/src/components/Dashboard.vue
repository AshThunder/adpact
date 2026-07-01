<template>
  <div class="dashboard-container w-full bg-canvas text-on-surface antialiased flex flex-col min-h-screen">
    <!-- Hero Banner -->
    <div class="w-full bg-surface-1 border-b border-hairline py-md md:py-xl">
      <div class="max-w-[1760px] mx-auto w-full px-md md:px-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-sm md:gap-md">
        <div>
          <span class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-xs">Influencer Escrow</span>
          <h1 class="font-display-md text-display-md text-primary dashboard-title">Creator Marketplace</h1>
        </div>
        <button 
          class="font-button text-body bg-primary text-on-primary px-8 py-4 rounded-xl flex items-center gap-2 hover:opacity-90 transition-opacity font-medium shadow-sm"
          @click="showCreateModal = true"
          id="btn-create-campaign-hero"
        >
          <span class="material-symbols-outlined text-[20px]">add</span>
          Create Campaign
        </button>
      </div>
    </div>

    <!-- No Contract Warning -->
    <div v-if="!contractAddress" class="mx-auto mt-md bg-fin-orange/10 border border-fin-orange/30 rounded-xl px-xl py-md flex items-center gap-md max-w-[1760px] w-full self-center">
      <span class="material-symbols-outlined text-fin-orange text-[24px]">warning</span>
      <div class="flex-1">
        <p class="font-body text-body text-primary font-medium">No contract deployed on this network</p>
        <p class="font-body text-body-sm text-ink-subtle">Switch to <strong>StudioNet</strong> or <strong>Bradbury</strong> in the network dropdown to interact with the deployed escrow contract.</p>
      </div>
    </div>

    <!-- Main Layout Grid -->
    <div class="flex flex-col md:flex-row p-md md:p-xl gap-md md:gap-xl max-w-[1760px] mx-auto w-full flex-grow">
      <!-- Sidebar Navigation -->
      <aside class="w-full md:w-72 flex-shrink-0 flex flex-col gap-md">
        <!-- Virtual Escrow Balance Card -->
        <div v-if="props.account" class="bg-surface-1 border border-hairline rounded-2xl p-lg flex flex-col gap-md shadow-sm">
          <div class="flex items-center justify-between">
            <span class="font-eyebrow text-[11px] text-ink-subtle uppercase tracking-wider font-semibold">Virtual Escrow Balance</span>
            <span class="material-symbols-outlined text-[20px] text-ink-subtle">account_balance_wallet</span>
          </div>
          <div class="flex flex-col">
            <span class="font-headline text-display-sm text-primary font-bold">{{ formattedUserBalance }} GEN</span>
            <span class="text-[10px] text-ink-muted mt-1">Earned payouts & refunded budgets</span>
          </div>
          <button 
            @click="withdrawBalance"
            :disabled="withdrawing || userBalanceRaw === '0'"
            class="w-full font-button text-body-sm bg-primary text-on-primary py-2.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-surface-3 disabled:text-ink-subtle/60 border border-hairline/20 shadow-sm"
          >
            <div v-if="withdrawing" class="spinner border-2 border-on-primary border-t-transparent w-4 h-4 rounded-full animate-spin"></div>
            <span v-else>Withdraw to Wallet</span>
          </button>
        </div>

        <!-- Scrollable Navigation Buttons Row -->
        <div class="flex flex-row md:flex-col gap-sm overflow-x-auto scrollbar-none pb-sm md:pb-0 w-full">
          <button 
            class="flex items-center gap-3 p-3 md:p-md rounded-xl transition-all font-body text-body text-left whitespace-nowrap flex-shrink-0 md:justify-between"
            :class="selectedTab === 'all' && !selectedCampaign ? 'bg-surface-container-highest text-primary font-medium border border-hairline' : 'text-ink-subtle hover:bg-surface-container border border-transparent'"
            @click="selectTab('all')"
            id="btn-tab-all-campaigns"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[22px]">grid_view</span>
              All Campaigns
            </div>
            <span 
              class="px-2.5 py-0.5 rounded-full text-body-sm font-mono border transition-all"
              :class="selectedTab === 'all' && !selectedCampaign ? 'bg-surface-1 border-hairline text-primary' : 'bg-surface-2 border-transparent text-ink-subtle'"
            >
              {{ campaigns.length }}
            </span>
          </button>
          <button 
            class="flex items-center gap-3 p-3 md:p-md rounded-xl transition-all font-body text-body text-left whitespace-nowrap flex-shrink-0 md:justify-between"
            :class="selectedTab === 'my_campaigns' && !selectedCampaign ? 'bg-surface-container-highest text-primary font-medium border border-hairline' : 'text-ink-subtle hover:bg-surface-container border border-transparent'"
            @click="selectTab('my_campaigns')"
            id="btn-tab-my-campaigns"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[22px]">folder</span>
              My Campaigns
            </div>
            <span 
              class="px-2.5 py-0.5 rounded-full text-body-sm font-mono border transition-all"
              :class="selectedTab === 'my_campaigns' && !selectedCampaign ? 'bg-surface-1 border-hairline text-primary' : 'bg-surface-2 border-transparent text-ink-subtle'"
            >
              {{ advertiserCampaignsCount }}
            </span>
          </button>
          <button 
            class="flex items-center gap-3 p-3 md:p-md rounded-xl transition-all font-body text-body text-left whitespace-nowrap flex-shrink-0 md:justify-between"
            :class="selectedTab === 'analytics' && !selectedCampaign ? 'bg-surface-container-highest text-primary font-medium border border-hairline' : 'text-ink-subtle hover:bg-surface-container border border-transparent'"
            @click="selectTab('analytics')"
            id="btn-tab-analytics"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[22px]">analytics</span>
              Analytics
            </div>
          </button>

          <!-- Divider (Desktop Only) -->
          <div class="hidden md:block border-t border-hairline my-xs"></div>

          <button 
            class="flex items-center gap-3 p-3 md:p-md rounded-xl transition-all font-body text-body text-left whitespace-nowrap flex-shrink-0 md:justify-between"
            :class="selectedTab === 'my_applications' && !selectedCampaign ? 'bg-surface-container-highest text-primary font-medium border border-hairline' : 'text-ink-subtle hover:bg-surface-container border border-transparent'"
            @click="selectTab('my_applications')"
            id="btn-tab-my-applications"
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-[22px]">assignment_turned_in</span>
              My Applications
            </div>
            <span 
              class="px-2.5 py-0.5 rounded-full text-body-sm font-mono border transition-all"
              :class="selectedTab === 'my_applications' && !selectedCampaign ? 'bg-surface-1 border-hairline text-primary' : 'bg-surface-2 border-transparent text-ink-subtle'"
            >
              {{ userApplications.length }}
            </span>
          </button>
        </div>
      </aside>

      <!-- Main Panel Display -->
      <main class="flex-grow">
        <!-- Campaign Detail View -->
        <div v-if="selectedCampaign" class="detail-container">
          <CampaignDetail 
            :campaign="selectedCampaign" 
            :account="account" 
            :escrow="escrow" 
            @refresh="fetchData"
            @back="selectedCampaign = null"
          />
        </div>

        <!-- Analytics Dashboard View -->
        <div v-else-if="selectedTab === 'analytics'" class="space-y-xl">
          <div class="flex justify-between items-center border-b border-hairline pb-lg">
            <div>
              <p class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider mb-xs">Protocol Overview</p>
              <h2 class="font-display-md text-display-md text-primary" style="font-size:32px;">Influencer Escrow Analytics</h2>
            </div>
            <div v-if="loading" class="spinner border-2 border-primary border-t-transparent w-5 h-5 rounded-full animate-spin"></div>
          </div>

          <!-- Stats Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-xl">
            <!-- TVL Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start text-ink-subtle mb-lg">
                <span class="font-eyebrow text-caption uppercase tracking-wider font-medium text-ink-muted">Total Value Locked (TVL)</span>
                <span class="material-symbols-outlined text-[26px] text-fin-orange">lock</span>
              </div>
              <div>
                <p class="font-headline text-display-md text-primary mb-sm font-semibold">
                  {{ formatGen(totalValueLocked) }} GEN
                </p>
                <span class="text-caption text-report-green flex items-center gap-1 font-medium">
                  <span class="material-symbols-outlined text-sm">trending_up</span>
                  +12.4% this week
                </span>
              </div>
            </div>

            <!-- Active Campaigns Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start text-ink-subtle mb-lg">
                <span class="font-eyebrow text-caption uppercase tracking-wider font-medium text-ink-muted">Active Campaigns</span>
                <span class="material-symbols-outlined text-[26px] text-primary">campaign</span>
              </div>
              <div>
                <p class="font-headline text-display-md text-primary mb-sm font-semibold">
                  {{ campaigns.length }}
                </p>
                <span class="text-caption text-ink-subtle">
                  Across 3 media platforms
                </span>
              </div>
            </div>

            <!-- Slots filled Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start text-ink-subtle mb-lg">
                <span class="font-eyebrow text-caption uppercase tracking-wider font-medium text-ink-muted">Active Collaborations</span>
                <span class="material-symbols-outlined text-[26px] text-report-green">handshake</span>
              </div>
              <div>
                <p class="font-headline text-display-md text-primary mb-sm font-semibold">
                  {{ totalSlotsFilled }} / {{ totalMaxSlots }}
                </p>
                <!-- CSS progress bar -->
                <div class="w-full bg-surface-2 h-2 rounded-full overflow-hidden mt-sm">
                  <div 
                    class="bg-report-green h-full rounded-full transition-all" 
                    :style="`width: ${totalMaxSlots > 0 ? (totalSlotsFilled / totalMaxSlots) * 100 : 0}%`"
                  ></div>
                </div>
              </div>
            </div>

            <!-- Avg Budget Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow">
              <div class="flex justify-between items-start text-ink-subtle mb-lg">
                <span class="font-eyebrow text-caption uppercase tracking-wider font-medium text-ink-muted">Avg Creator Budget</span>
                <span class="material-symbols-outlined text-[26px] text-primary">payments</span>
              </div>
              <div>
                <p class="font-headline text-display-md text-primary mb-sm font-semibold">
                  {{ formatGen(avgCampaignBudget) }} GEN
                </p>
                <span class="text-caption text-ink-subtle">
                  Per approved slot
                </span>
              </div>
            </div>
          </div>

          <!-- Details Section -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-xl">
            <!-- Platform Share Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl shadow-sm hover:shadow-md transition-shadow">
              <h3 class="font-headline text-headline text-primary mb-lg">Platform Distribution</h3>
              <div class="space-y-lg">
                <!-- Twitter -->
                <div>
                  <div class="flex justify-between text-body mb-sm">
                    <span class="flex items-center gap-xs text-primary font-medium">
                      <span class="material-symbols-outlined text-[20px] text-ink-subtle">tag</span>
                      Twitter / X
                    </span>
                    <span class="font-semibold text-primary">{{ platformPercentages.twitter }}%</span>
                  </div>
                  <div class="w-full bg-surface-2 h-3 rounded-full overflow-hidden">
                    <div class="bg-primary h-full rounded-full" :style="`width: ${platformPercentages.twitter}%`"></div>
                  </div>
                </div>
                <!-- YouTube -->
                <div>
                  <div class="flex justify-between text-body mb-sm">
                    <span class="flex items-center gap-xs text-primary font-medium">
                      <span class="material-symbols-outlined text-[20px] text-ink-subtle">play_circle</span>
                      YouTube
                    </span>
                    <span class="font-semibold text-primary">{{ platformPercentages.youtube }}%</span>
                  </div>
                  <div class="w-full bg-surface-2 h-3 rounded-full overflow-hidden">
                    <div class="bg-fin-orange h-full rounded-full" :style="`width: ${platformPercentages.youtube}%`"></div>
                  </div>
                </div>
                <!-- Newsletter -->
                <div>
                  <div class="flex justify-between text-body mb-sm">
                    <span class="flex items-center gap-xs text-primary font-medium">
                      <span class="material-symbols-outlined text-[20px] text-ink-subtle">history_edu</span>
                      Newsletter
                    </span>
                    <span class="font-semibold text-primary">{{ platformPercentages.newsletter }}%</span>
                  </div>
                  <div class="w-full bg-surface-2 h-3 rounded-full overflow-hidden">
                    <div class="bg-report-green h-full rounded-full" :style="`width: ${platformPercentages.newsletter}%`"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Consensus Stats Card -->
            <div class="bg-surface-1 border border-hairline rounded-2xl p-xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
              <div>
                <h3 class="font-headline text-headline text-primary mb-sm">AI Consensus Settlement</h3>
                <p class="text-body text-ink-subtle mb-xl">
                  All sponsorships are monitored and validated by GenLayer's network of decentralized AI agents.
                </p>
              </div>
              <div class="grid grid-cols-3 gap-lg border-t border-hairline pt-xl">
                <div class="text-center">
                  <span class="font-eyebrow text-caption text-ink-subtle block mb-2 font-medium tracking-wide">SETTLEMENT SPEED</span>
                  <span class="font-headline text-headline text-primary font-semibold">&lt; 30s</span>
                </div>
                <div class="text-center border-x border-hairline">
                  <span class="font-eyebrow text-caption text-ink-subtle block mb-2 font-medium tracking-wide">VALIDATOR RATE</span>
                  <span class="font-headline text-headline text-report-green font-semibold">99.8%</span>
                </div>
                <div class="text-center">
                  <span class="font-eyebrow text-caption text-ink-subtle block mb-2 font-medium tracking-wide">ESCROW SAFETY</span>
                  <span class="font-headline text-headline text-primary font-semibold">100%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- My Applications View -->
        <div v-else-if="selectedTab === 'my_applications'" class="space-y-xl">
          <div class="flex justify-between items-center border-b border-hairline pb-lg">
            <div>
              <p class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider mb-xs">Creator Hub</p>
              <h2 class="font-headline text-headline text-primary">My Applications & Collaborations</h2>
            </div>
            <div v-if="loadingApplications" class="spinner border-2 border-primary border-t-transparent w-5 h-5 rounded-full animate-spin"></div>
          </div>

          <!-- Empty State -->
          <div v-if="!loadingApplications && userApplications.length === 0" class="bg-surface-1 border border-hairline border-dashed rounded-2xl p-xxl flex flex-col items-center justify-center text-center min-h-[300px]">
            <span class="material-symbols-outlined text-[56px] text-ink-subtle mb-lg">assignment</span>
            <h3 class="font-headline text-headline text-primary mb-sm">No Applications Yet</h3>
            <p class="font-body text-body text-ink-subtle max-w-md mb-lg">
              You haven't applied to any campaigns yet. Browse the marketplace to find opportunities and apply.
            </p>
            <button 
              class="font-button text-body bg-primary text-on-primary px-6 py-3 rounded-xl flex items-center gap-2 hover:opacity-90 transition-opacity shadow-sm"
              @click="selectTab('all')"
            >
              <span class="material-symbols-outlined text-[18px]">explore</span>
              Browse Marketplace
            </button>
          </div>

          <!-- Applications Grid -->
          <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-md md:gap-xl">
            <div 
              v-for="item in userApplications" 
              :key="item.id" 
              class="bg-surface-1 border border-hairline rounded-2xl p-md md:p-xl hover:shadow-md transition-all flex flex-col h-full cursor-pointer hover:-translate-y-[2px] duration-200"
              @click="selectedCampaign = item"
            >
              <div class="flex items-start justify-between mb-sm md:mb-lg">
                <span class="bg-surface-container px-3 py-1 md:px-4 md:py-2 rounded-full font-button text-caption text-primary flex items-center gap-1.5 border border-hairline">
                  <span class="material-symbols-outlined text-[16px]">tag</span>
                  {{ item.platform ? item.platform.toUpperCase() : 'TWITTER' }}
                </span>
                
                <!-- Status Badge -->
                <span 
                  class="px-2.5 py-0.5 md:px-3 md:py-1 rounded-full font-mono text-[10px] md:text-[11px] uppercase font-bold border"
                  :class="item.userStatus === 'collaborating' ? 'bg-report-green/10 border-report-green/20 text-report-green' : (item.userStatus === 'applied' ? 'bg-fin-orange/10 border-fin-orange/20 text-fin-orange' : 'bg-report-blue/10 border-report-blue/20 text-report-blue')"
                >
                  {{ item.userStatus === 'collaborating' ? 'Active Collab' : (item.userStatus === 'applied' ? 'Pending' : item.userStatus) }}
                </span>
              </div>

              <h3 class="font-headline text-headline text-primary mb-xs md:mb-md leading-tight card-title">
                {{ item.title }}
              </h3>
              
              <p class="font-body text-body text-ink-subtle mb-md md:mb-xl line-clamp-2 flex-grow">
                {{ item.description }}
              </p>

              <div class="border-t border-hairline pt-md md:pt-lg flex justify-between items-center">
                <div>
                  <span class="font-eyebrow text-caption text-ink-muted block mb-1">YOUR ROLE</span>
                  <span class="font-subhead text-subhead font-medium text-primary">
                    {{ item.userStatus === 'collaborating' ? 'Creator' : 'Applicant' }}
                  </span>
                </div>
                <div class="text-right">
                  <span class="font-eyebrow text-caption text-ink-muted block mb-1">BUDGET</span>
                  <span class="font-subhead text-subhead font-medium text-primary">
                    {{ formatGen(item.atto_budget_per_creator) }} GEN
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Campaign List View -->
        <div v-else class="space-y-lg">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-md">
            <h2 class="font-subhead text-subhead text-primary">
              {{ selectedTab === 'all' ? 'All Opportunities' : 'My Managed Campaigns' }}
            </h2>
            
            <div class="flex items-center gap-1 bg-surface-2 p-1 rounded-lg border border-hairline w-full md:w-auto">
              <button 
                @click="statusFilter = 'active'"
                :class="statusFilter === 'active' ? 'bg-surface-1 shadow-sm text-primary font-medium' : 'text-ink-subtle hover:text-primary'"
                class="flex-1 md:flex-none px-4 py-1.5 rounded-md text-body-sm transition-all text-center"
              >Active</button>
              <button 
                @click="statusFilter = 'ended'"
                :class="statusFilter === 'ended' ? 'bg-surface-1 shadow-sm text-primary font-medium' : 'text-ink-subtle hover:text-primary'"
                class="flex-1 md:flex-none px-4 py-1.5 rounded-md text-body-sm transition-all text-center"
              >Ended</button>
            </div>
            <div v-if="loading" class="spinner border-2 border-primary border-t-transparent w-4 h-4 rounded-full animate-spin hidden md:block"></div>
          </div>

          <!-- Search & Filter Controls -->
          <div class="bg-surface-1 border border-hairline p-lg rounded-2xl flex flex-col md:flex-row gap-lg items-center justify-between shadow-sm">
            <!-- Search bar -->
            <div class="relative w-full md:w-96">
              <span class="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-subtle text-[22px]">search</span>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search campaigns..." 
                class="w-full pl-11 pr-5 py-3 bg-surface-2 border border-hairline rounded-xl text-body text-primary placeholder-ink-subtle focus:outline-none focus:border-primary transition-colors focus:ring-0"
              />
            </div>
            
            <!-- Platform filter pills & Sort -->
            <div class="flex flex-wrap items-center gap-sm w-full md:w-auto">
              <!-- Sort Dropdown -->
              <div class="relative flex items-center bg-surface-2 border border-hairline rounded-xl px-3 py-2 mr-2 transition-colors hover:bg-surface-3">
                <span class="material-symbols-outlined text-[18px] text-ink-subtle mr-2">sort</span>
                <select v-model="sortOption" class="bg-transparent text-body-sm text-primary font-medium focus:outline-none cursor-pointer appearance-none pr-5 w-full">
                  <option value="time">Latest First</option>
                  <option value="amount">Highest Budget</option>
                  <option value="name">Name (A-Z)</option>
                </select>
                <span class="material-symbols-outlined text-[16px] text-ink-subtle absolute right-2 pointer-events-none">expand_more</span>
              </div>

              <!-- Platform Pills -->
              <button 
                v-for="plat in ['all', 'twitter', 'youtube', 'newsletter']"
                :key="plat"
                :disabled="plat !== 'all' && plat !== 'twitter'"
                @click="(plat === 'all' || plat === 'twitter') && (selectedPlatform = plat)"
                class="px-4 py-2 rounded-full font-button text-caption border transition-all flex items-center gap-1"
                :class="selectedPlatform === plat ? 'bg-primary border-primary text-on-primary font-medium shadow-sm' : (plat !== 'all' && plat !== 'twitter' ? 'bg-surface-2/40 border-hairline/50 text-ink-subtle/40 cursor-not-allowed opacity-50' : 'bg-surface-2 border-hairline text-ink-subtle hover:bg-surface-container-highest')"
              >
                {{ plat === 'all' ? 'All Platforms' : (plat === 'twitter' ? 'X / Twitter' : plat.charAt(0).toUpperCase() + plat.slice(1)) }}
                <span v-if="plat !== 'all' && plat !== 'twitter'" class="text-[9px] bg-ink-subtle/10 px-1 py-0.5 rounded font-normal lowercase">Soon</span>
              </button>
            </div>
          </div>

          <!-- Empty State -->
          <div 
            v-if="filteredCampaigns.length === 0" 
            class="bg-surface-1 border border-hairline border-dashed rounded-xl p-xl flex flex-col items-center justify-center text-center min-h-[300px]"
          >
            <span class="material-symbols-outlined text-[48px] text-ink-subtle mb-md">folder_open</span>
            <h3 class="font-subhead text-subhead text-primary mb-xs">No Campaigns Found</h3>
            <p class="font-body-sm text-body-sm text-ink-subtle max-w-md">
              There are currently no active campaigns matching your selection. Get started by creating your first escrow-backed campaign.
            </p>
            <button 
              class="font-button text-button bg-primary text-on-primary px-4 py-2 rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity mt-md"
              @click="showCreateModal = true"
              id="btn-empty-create"
            >
              <span class="material-symbols-outlined text-[16px]">add</span>
              Create Campaign
            </button>
          </div>

          <!-- Campaigns Grid -->
          <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-md md:gap-xl">
            <div 
              v-for="camp in filteredCampaigns" 
              :key="camp.id" 
              class="bg-surface-1 border border-hairline rounded-2xl p-md md:p-xl hover:shadow-md transition-all flex flex-col h-full cursor-pointer hover:-translate-y-[2px] duration-200"
              @click="selectedCampaign = camp"
              :id="`campaign-card-${camp.id}`"
            >
              <div class="flex items-start justify-between mb-sm md:mb-lg">
                <span class="bg-surface-container px-3 py-1.5 md:px-4 md:py-2 rounded-full font-button text-caption text-primary flex items-center gap-1.5 border border-hairline">
                  <span class="material-symbols-outlined text-[16px]">
                    {{ camp.platform && camp.platform.toLowerCase() === 'youtube' ? 'play_circle' : (camp.platform && camp.platform.toLowerCase() === 'newsletter' ? 'history_edu' : 'tag') }}
                  </span>
                  {{ camp.platform ? camp.platform.toUpperCase() : 'Twitter' }}
                </span>
                
                <span 
                  v-if="camp.posting_deadline && new Date() > new Date(camp.posting_deadline)" 
                  class="bg-error/10 border border-error/20 text-error px-2 py-0.5 md:px-2.5 md:py-1 rounded font-mono text-[10px] md:text-[11px] uppercase font-bold"
                >
                  Expired
                </span>
                <span 
                  v-else-if="camp.advertiser.toLowerCase() === account.address.toLowerCase()" 
                  class="bg-report-green/10 border border-report-green/20 text-report-green px-2 py-0.5 md:px-2.5 md:py-1 rounded font-mono text-[10px] md:text-[11px] uppercase font-bold"
                >
                  Advertiser
                </span>
                <span v-else class="font-mono text-mono text-ink-subtle text-[12px] md:text-[13px]">Active</span>
              </div>

              <h3 class="font-headline text-headline text-primary mb-xs md:mb-md leading-tight card-title">
                {{ camp.title }}
              </h3>
              
              <p class="font-body text-body text-ink-subtle mb-md md:mb-xl line-clamp-3 flex-grow">
                {{ camp.description }}
              </p>

              <div class="border-t border-hairline pt-md md:pt-lg flex justify-between items-center">
                <div>
                  <span class="font-eyebrow text-caption text-ink-muted block mb-1">BUDGET PER CREATOR</span>
                  <span class="font-subhead text-subhead font-medium text-primary">
                    {{ formatGen(camp.atto_budget_per_creator) }} GEN
                  </span>
                </div>
                <div class="text-right">
                  <span class="font-eyebrow text-caption text-ink-muted block mb-1">SLOTS</span>
                  <span class="font-subhead text-subhead font-medium text-primary">
                    {{ camp.active_creators_count }} / {{ camp.max_creators }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Create Campaign Modal -->
    <CreateCampaign 
      v-if="showCreateModal" 
      :escrow="escrow" 
      @close="showCreateModal = false" 
      @created="fetchData" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { Plus, Grid, FolderOpen, ArrowLeft } from 'lucide-vue-next';
import InfluencerEscrow from '../logic/InfluencerEscrow.js';
import CreateCampaign from './CreateCampaign.vue';
import CampaignDetail from './CampaignDetail.vue';
import { selectedNetwork } from '../services/genlayer.js';
import { getContractAddress } from '../services/contract_addresses.js';

const props = defineProps({
  account: Object,
  activeTab: {
    type: String,
    default: 'all'
  }
});

const emit = defineEmits(['update:activeTab']);

const escrow = ref(null);
const campaigns = ref([]);
const loading = ref(false);
const loadingApplications = ref(false);
const showCreateModal = ref(false);
const selectedCampaign = ref(null);
const userApplications = ref([]);
const selectedTab = ref(props.activeTab);

const userBalanceRaw = ref("0");
const withdrawing = ref(false);

const formattedUserBalance = computed(() => {
  if (!userBalanceRaw.value || userBalanceRaw.value === "0") return "0.00";
  return (Number(userBalanceRaw.value) / 1e18).toFixed(2);
});

async function fetchUserBalance() {
  if (!escrow.value || !props.account || !props.account.address) {
    userBalanceRaw.value = "0";
    return;
  }
  try {
    userBalanceRaw.value = await escrow.value.getBalance(props.account.address);
  } catch (err) {
    console.error("Failed to fetch user balance:", err);
    userBalanceRaw.value = "0";
  }
}

async function withdrawBalance() {
  if (!escrow.value || userBalanceRaw.value === "0") return;
  withdrawing.value = true;
  try {
    await escrow.value.withdrawBalance();
    // Refresh balance and campaigns
    await Promise.all([fetchUserBalance(), fetchData()]);
  } catch (err) {
    console.error("Withdrawal failed:", err);
    alert("Withdrawal failed: " + (err.message || err));
  } finally {
    withdrawing.value = false;
  }
}

// Watch for tab change from prop (parent top-nav click)
watch(() => props.activeTab, (newTab) => {
  if (newTab && newTab !== selectedTab.value) {
    selectedTab.value = newTab;
    selectedCampaign.value = null;
  }
});

function selectTab(tabName) {
  selectedTab.value = tabName;
  selectedCampaign.value = null;
  emit('update:activeTab', tabName);
}

// Reactive contract address for the current network (used for warning banner)
const contractAddress = computed(() => getContractAddress(selectedNetwork.value));

// Initialize contract wrapper
function initContract() {
  const contractAddress = getContractAddress(selectedNetwork.value);
  console.log(`Initializing contract wrapper on ${selectedNetwork.value} at address ${contractAddress}`);
  // Pass string address to InfluencerEscrow
  const userAddress = props.account ? props.account.address : null;
  escrow.value = new InfluencerEscrow(contractAddress, userAddress);
}

// Watch for account change
watch(() => props.account, (newAcc) => {
  const userAddress = newAcc ? newAcc.address : null;
  if (escrow.value) {
    escrow.value.updateAccount(userAddress);
  } else {
    initContract();
  }
  fetchData();
  fetchUserBalance();
}, { deep: true });

// Watch for network change
watch(selectedNetwork, () => {
  selectedCampaign.value = null;
  initContract();
  fetchData();
  fetchUserBalance();
});

async function fetchData() {
  if (!escrow.value || !escrow.value.contractAddress) {
    campaigns.value = [];
    userApplications.value = [];
    return;
  }
  loading.value = true;
  try {
    const rawCampaigns = await escrow.value.getCampaigns();
    campaigns.value = rawCampaigns;

    // Refresh selected campaign if it is currently open
    if (selectedCampaign.value) {
      const updated = rawCampaigns.find(c => c.id === selectedCampaign.value.id);
      if (updated) {
        selectedCampaign.value = updated;
      }
    }

    // Fetch user's applications and balance in the background
    if (props.account && props.account.address) {
      fetchUserApplications(rawCampaigns);
      fetchUserBalance();
    }
  } catch (err) {
    console.error('Fetch campaigns failed:', err);
    campaigns.value = [];
  } finally {
    loading.value = false;
  }
}

async function fetchUserApplications(campaignList) {
  if (!escrow.value || !props.account) return;
  loadingApplications.value = true;
  const results = [];
  const addr = props.account.address.toLowerCase();
  try {
    for (const camp of campaignList) {
      try {
        const apps = await escrow.value.getApplications(camp.id);
        const collabs = await escrow.value.getCollaborations(camp.id);
        const hasApplied = apps.some(a => a.creator && a.creator.toLowerCase() === addr);
        const userCollab = collabs.find(c => c.creator && c.creator.toLowerCase() === addr);
        if (hasApplied || userCollab) {
          results.push({
            ...camp,
            userStatus: userCollab ? 'collaborating' : 'applied',
            userCollaboration: userCollab || null,
          });
        }
      } catch (e) {
        console.warn(`Could not fetch apps/collabs for campaign ${camp.id}:`, e);
      }
    }
    userApplications.value = results;
  } catch (err) {
    console.error('Failed to fetch user applications:', err);
  } finally {
    loadingApplications.value = false;
  }
}

const advertiserCampaignsCount = computed(() => {
  if (!props.account) return 0;
  return campaigns.value.filter(c => c.advertiser.toLowerCase() === props.account.address.toLowerCase()).length;
});

const searchQuery = ref('');
const selectedPlatform = ref('all');
const statusFilter = ref('active');
const sortOption = ref('time');

const filteredCampaigns = computed(() => {
  let list = campaigns.value;

  // 1. Tab filter
  if (selectedTab.value === 'my_campaigns') {
    list = list.filter(c => c.advertiser.toLowerCase() === props.account.address.toLowerCase());
  }

  // 2. Status filter (Active vs Ended)
  list = list.filter(c => {
    const isExpired = c.posting_deadline && new Date() > new Date(c.posting_deadline);
    const isEnded = c.status === 'CLOSED' || c.status === 'CANCELLED' || isExpired;
    if (statusFilter.value === 'active') return !isEnded;
    return isEnded;
  });

  // 3. Platform filter
  if (selectedPlatform.value !== 'all') {
    list = list.filter(c => c.platform && c.platform.toLowerCase() === selectedPlatform.value.toLowerCase());
  }

  // 4. Search text query filter
  if (searchQuery.value.trim() !== '') {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(c => 
      (c.title && c.title.toLowerCase().includes(q)) || 
      (c.description && c.description.toLowerCase().includes(q))
    );
  }

  // 5. Sorting
  list = [...list].sort((a, b) => {
    if (sortOption.value === 'time') {
      const idA = Number((a.id || '').replace('camp_', '')) || 0;
      const idB = Number((b.id || '').replace('camp_', '')) || 0;
      return idB - idA; // Latest first
    } else if (sortOption.value === 'amount') {
      const budgetA = BigInt(a.atto_budget_per_creator || 0);
      const budgetB = BigInt(b.atto_budget_per_creator || 0);
      return budgetB > budgetA ? 1 : budgetB < budgetA ? -1 : 0; // Highest first
    } else if (sortOption.value === 'name') {
      const nameA = (a.title || '').toLowerCase();
      const nameB = (b.title || '').toLowerCase();
      return nameA.localeCompare(nameB); // A-Z
    }
    return 0;
  });

  return list;
});

const totalValueLocked = computed(() => {
  return campaigns.value.reduce((acc, c) => {
    const budget = BigInt(c.atto_budget_per_creator || 0);
    const maxC = BigInt(c.max_creators || 0);
    return acc + (budget * maxC);
  }, 0n);
});

const totalSlotsFilled = computed(() => {
  return campaigns.value.reduce((acc, c) => acc + Number(c.active_creators_count || 0), 0);
});

const totalMaxSlots = computed(() => {
  return campaigns.value.reduce((acc, c) => acc + Number(c.max_creators || 0), 0);
});

const avgCampaignBudget = computed(() => {
  if (campaigns.value.length === 0) return 0n;
  const total = campaigns.value.reduce((acc, c) => acc + BigInt(c.atto_budget_per_creator || 0), 0n);
  return total / BigInt(campaigns.value.length);
});

const platformPercentages = computed(() => {
  const total = campaigns.value.length;
  if (total === 0) return { twitter: 0, youtube: 0, newsletter: 0 };

  const twitter = campaigns.value.filter(c => !c.platform || c.platform.toLowerCase() === 'twitter' || c.platform.toLowerCase() === 'x').length;
  const youtube = campaigns.value.filter(c => c.platform && c.platform.toLowerCase() === 'youtube').length;
  const newsletter = campaigns.value.filter(c => c.platform && c.platform.toLowerCase() === 'newsletter').length;

  const tPercent = Math.round((twitter / total) * 100);
  const yPercent = Math.round((youtube / total) * 100);
  const nPercent = Math.round((newsletter / total) * 100);

  return {
    twitter: tPercent,
    youtube: yPercent,
    newsletter: nPercent
  };
});

function formatGen(atto) {
  if (!atto) return '0';
  return (Number(atto) / 1e18).toFixed(2);
}

onMounted(() => {
  initContract();
  fetchData();
  fetchUserBalance();
});
</script>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.scrollbar-none {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.dashboard-container {
  min-height: 80vh;
}

.card-title {
  font-size: 20px !important;
}

.dashboard-title {
  font-size: 28px;
}

@media (max-width: 768px) {
  .card-title {
    font-size: 16px !important;
  }
  .dashboard-title {
    font-size: 20px;
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--space-xl);
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.campaign-nav-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xxs);
}

.campaign-nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: transparent;
  color: var(--color-steel);
  font-family: var(--font-body);
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: var(--rounded-sm);
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  width: 100%;
}

.campaign-nav-item:hover {
  background: var(--color-surface-soft);
  color: var(--color-ink);
}

.campaign-nav-item.active {
  background: var(--color-canvas);
  color: var(--color-ink);
  font-weight: 600;
  box-shadow: var(--shadow-subtle);
}

.campaign-count-badge {
  margin-left: auto;
  background: var(--color-surface);
  color: var(--color-steel);
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--rounded-full);
}

.campaign-nav-item.active .campaign-count-badge {
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.campaign-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
}

.campaign-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.text-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
