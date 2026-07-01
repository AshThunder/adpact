<template>
  <div class="campaign-detail w-full bg-canvas text-on-surface font-body antialiased">
    <!-- Breadcrumb / Back Action -->
    <div class="mb-md md:mb-xl flex items-center gap-xs text-ink-subtle hover:text-primary transition-colors cursor-pointer w-fit group" @click="$emit('back')">
      <span class="material-symbols-outlined text-[18px] group-hover:-translate-x-1 transition-transform">arrow_back</span>
      <span class="font-body text-body-sm font-medium tracking-tight uppercase tracking-wider font-bold">Back to My Campaigns</span>
    </div>

    <!-- ADVERTISER VIEW (Full width, premium bento grid layout) -->
    <div v-if="isAdvertiser" class="space-y-8 md:space-y-16">
      <!-- Header Section -->
      <section class="space-y-lg">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-md border-b border-hairline pb-lg">
          <div class="space-y-sm">
            <p class="font-eyebrow text-eyebrow text-ink-subtle uppercase tracking-widest">Campaign Details</p>
            <h1 class="font-display-md text-display-md text-primary text-[22px] md:text-[32px]">{{ campaign.title }}</h1>
            <div class="flex flex-wrap items-center gap-sm mt-xs">
              <span v-if="isExpired" class="inline-flex items-center px-sm py-xxs rounded-full bg-error-container/10 border border-error-container/30 font-mono text-mono text-error">
                <span class="w-2 h-2 rounded-full bg-error mr-2"></span>
                Expired
              </span>
              <span v-else class="inline-flex items-center px-sm py-xxs rounded-full bg-surface-container-highest border border-hairline font-mono text-mono text-ink-subtle">
                <span class="w-2 h-2 rounded-full bg-fin-orange mr-2"></span>
                {{ campaign.status === 'OPEN_FOR_APPLICATIONS' ? 'Reviewing Applications' : 'Reviewing Collaborations' }}
              </span>
              <span class="font-body text-body-sm text-ink-subtle flex items-center gap-xs">
                <span class="material-symbols-outlined text-sm">schedule</span>
                Deadline: {{ formatDate(campaign.posting_deadline).split(',')[0] }}
              </span>
            </div>
          </div>
          <div class="flex gap-sm">
            <button 
              class="px-md py-sm bg-surface-1 border border-hairline rounded-lg font-button text-button text-primary hover:bg-surface-container transition-colors shadow-sm"
              @click="simulateAdvertiserAction('Edit Brief')"
            >
              Edit Brief
            </button>
            <button 
              class="px-md py-sm bg-surface-1 border border-hairline rounded-lg font-button text-button text-error hover:bg-error-container transition-colors shadow-sm"
              @click="simulateAdvertiserAction('Pause Campaign')"
            >
              Pause Campaign
            </button>
          </div>
        </div>
      </section>

      <!-- Requirements Card (Editorial Style) -->
      <section class="bg-surface-1 border border-hairline rounded-xl p-lg md:p-xl grid grid-cols-1 md:grid-cols-3 gap-xl">
        <div class="space-y-xs">
          <h3 class="font-eyebrow text-eyebrow text-ink-subtle">Total Escrow Budget</h3>
          <p class="font-card-title text-card-title text-primary">
            {{ formatGen(campaign.atto_budget_per_creator * campaign.max_creators) }} GEN
          </p>
          <p class="font-mono text-mono text-ink-subtle break-all">{{ campaign.id }}</p>
        </div>
        <div class="space-y-xs border-t md:border-t-0 md:border-l border-hairline pt-md md:pt-0 md:pl-xl">
          <h3 class="font-eyebrow text-eyebrow text-ink-subtle">Target Audience &amp; Description</h3>
          <p class="font-body text-body text-primary leading-snug">{{ campaign.description }}</p>
          <p class="font-body text-body-sm text-ink-subtle">Platform: {{ campaign.platform ? campaign.platform.toUpperCase() : 'Twitter' }}</p>
        </div>
        <div class="space-y-xs border-t md:border-t-0 md:border-l border-hairline pt-md md:pt-0 md:pl-xl">
          <h3 class="font-eyebrow text-eyebrow text-ink-subtle">Deliverable Requirements</h3>
          <ul class="font-body text-body-sm text-primary space-y-1 list-disc list-inside">
            <li v-for="tag in parseArray(campaign.required_hashtags)" :key="tag">
              Must include hashtag: <strong>{{ tag }}</strong>
            </li>
            <li v-for="kw in parseArray(campaign.required_keywords)" :key="kw">
              Must contain keyword: <strong>{{ kw }}</strong>
            </li>
            <li v-if="parseArray(campaign.required_hashtags).length === 0 && parseArray(campaign.required_keywords).length === 0">
              No specific keyword constraints
            </li>
            <li>Includes AI-governed smart contract consensus check</li>
          </ul>
        </div>
      </section>

      <!-- Applications Received Section -->
      <section class="space-y-md">
        <div class="flex items-center justify-between">
          <h2 class="font-subhead text-subhead text-primary">
            Applications Received ({{ applications.filter(a => a.status === 'PENDING').length }})
          </h2>
        </div>
        
        <div class="bg-surface-1 border border-hairline rounded-xl overflow-hidden shadow-sm">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-surface-container-lowest border-b border-hairline">
                  <th class="font-eyebrow text-eyebrow text-ink-subtle font-medium p-md">Creator</th>
                  <th class="font-eyebrow text-eyebrow text-ink-subtle font-medium p-md hidden sm:table-cell">Wallet</th>
                  <th class="font-eyebrow text-eyebrow text-ink-subtle font-medium p-md">Proposal Snippet</th>
                  <th class="font-eyebrow text-eyebrow text-ink-subtle font-medium p-md text-right">Action</th>
                </tr>
              </thead>
              <tbody class="font-body text-body-sm divide-y divide-hairline">
                <tr v-if="applications.filter(a => a.status === 'PENDING').length === 0">
                  <td colspan="4" class="p-lg text-center text-ink-subtle font-body text-body-sm bg-surface-bright">
                    No applications received yet.
                  </td>
                </tr>
                <tr 
                  v-for="app in applications.filter(a => a.status === 'PENDING')" 
                  :key="app.creator" 
                  class="hover:bg-surface-container-low transition-colors group"
                >
                  <td class="p-md">
                    <div class="flex items-center gap-sm">
                      <div class="w-8 h-8 rounded-full bg-fin-orange/10 border border-fin-orange/20 text-fin-orange flex items-center justify-center font-bold text-xs">
                        {{ app.twitter_handle ? app.twitter_handle[0].toUpperCase() : 'C' }}
                      </div>
                      <span class="font-medium text-primary">@{{ app.twitter_handle }}</span>
                    </div>
                  </td>
                  <td class="p-md font-mono text-mono text-ink-subtle hidden sm:table-cell">
                    {{ app.creator.slice(0, 6) }}...{{ app.creator.slice(-4) }}
                  </td>
                  <td class="p-md text-ink-subtle max-w-xs truncate">
                    "{{ app.proposal_message }}"
                  </td>
                  <td class="p-md text-right">
                    <button 
                      class="bg-primary text-on-primary font-button text-button px-md py-xs rounded-lg hover:opacity-90 transition-opacity"
                      @click="approveCreator(app.creator)"
                      :disabled="actioning"
                    >
                      Approve
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Active Collaborations Section (Bento Grid) -->
      <section class="space-y-md">
        <div class="flex items-center justify-between border-b border-hairline pb-sm">
          <h2 class="font-subhead text-subhead text-primary">Active Collaborations</h2>
          <span class="font-mono text-mono text-ink-subtle">{{ collaborations.length }} In Progress</span>
        </div>

        <div v-if="collaborations.length === 0" class="text-ink-subtle font-body text-body-sm py-xl text-center bg-surface-bright rounded-xl border border-dashed border-hairline shadow-sm">
          No active collaborations are currently in progress.
        </div>

        <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-lg">
          <div 
            v-for="collab in collaborations" 
            :key="collab.creator" 
            class="bg-surface-1 border border-hairline rounded-xl p-lg flex flex-col justify-between hover:shadow-sm transition-shadow relative overflow-hidden"
          >
            <!-- Orange accent gradient for AI verification pending states -->
            <div v-if="collab.status === 'AI_VERIFICATION_PENDING'" class="absolute top-0 right-0 w-32 h-32 bg-fin-orange opacity-5 rounded-bl-full pointer-events-none"></div>

            <div class="space-y-md relative z-10">
              <div class="flex justify-between items-start">
                <div class="flex items-center gap-sm">
                  <div class="w-10 h-10 rounded-full bg-primary/5 border border-hairline text-primary flex items-center justify-center font-bold text-sm">
                    {{ getTwitterHandle(collab.creator)[0].toUpperCase() }}
                  </div>
                  <div>
                    <h3 class="font-body text-body font-medium text-primary">@{{ getTwitterHandle(collab.creator) }}</h3>
                    <p class="font-mono text-mono text-ink-subtle">Escrow: {{ formatGen(campaign.atto_budget_per_creator) }} GEN</p>
                  </div>
                </div>
                
                <!-- Status Badge -->
                <span 
                  class="px-sm py-xxs border rounded text-xs font-mono"
                  :class="{
                    'bg-secondary-fixed border-secondary-fixed-dim text-on-secondary-fixed': collab.status === 'AI_VERIFICATION_PENDING',
                    'bg-report-green/10 border-report-green/20 text-report-green': collab.status === 'RETENTION_MONITORING' || collab.status === 'FINALIZED' || collab.status === 'COMPLETED',
                    'bg-surface-container border-hairline text-ink-muted': collab.status !== 'AI_VERIFICATION_PENDING' && collab.status !== 'RETENTION_MONITORING' && collab.status !== 'FINALIZED' && collab.status !== 'COMPLETED'
                  }"
                >
                  {{ collab.status }}
                </span>
              </div>

              <!-- Draft Submitted text if exists -->
              <div v-if="collab.draft_text" class="bg-canvas border border-hairline rounded-lg p-md space-y-sm">
                <p class="font-eyebrow text-eyebrow text-ink-subtle">Draft Submission</p>
                <p class="font-body text-body-sm text-primary leading-relaxed">
                  "{{ collab.draft_text }}"
                </p>
                <a class="font-body text-body-sm text-brand-blue hover:underline inline-flex items-center gap-xs" href="#" @click.prevent="">
                  <span class="material-symbols-outlined text-[16px]">image</span> View attached media
                </a>
              </div>

              <!-- Live Tweet Link if exists -->
              <div v-if="collab.live_tweet_url" class="bg-canvas border border-hairline rounded-lg p-md space-y-sm">
                <div class="flex items-center gap-sm">
                  <span class="material-symbols-outlined text-ink-subtle text-[18px]">link</span>
                  <a class="font-mono text-mono text-brand-blue hover:underline truncate" :href="collab.live_tweet_url" target="_blank">
                    {{ collab.live_tweet_url }}
                  </a>
                </div>
                <p class="font-body text-body-sm text-ink-muted">
                  {{ collab.status === 'AI_VERIFICATION_PENDING' ? 'Creator has marked the post as live. Trigger the AI Oracle consensus review below to release the initial payout.' : 'Consensus successfully verified live tweet.' }}
                </p>
              </div>
            </div>

            <!-- Dynamic Interactive Actions based on Collab status -->
            <div class="flex flex-col gap-sm mt-lg pt-md border-t border-hairline relative z-10">
              
              <!-- 1. WAITING_ESCROW: Funding Escrow -->
              <button 
                v-if="collab.status === 'AWAITING_ESCROW_DEPOSIT'"
                class="w-full bg-fin-orange text-white font-button text-button py-sm rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-sm shadow-sm"
                @click="fundEscrow(collab.creator)"
                :disabled="actioning"
              >
                Fund Escrow Slot ({{ formatGen(campaign.atto_budget_per_creator) }} GEN)
              </button>

              <!-- 2. AWAITING_DRAFT_APPROVAL: Approve / Reject Draft -->
              <div v-if="collab.status === 'AWAITING_DRAFT_APPROVAL'" class="flex gap-sm w-full">
                <button 
                  class="flex-1 bg-primary text-on-primary font-button text-button py-sm rounded-lg hover:opacity-90 transition-opacity"
                  @click="approveDraft(collab.creator, true)"
                  :disabled="actioning"
                >
                  Approve Draft
                </button>
                <button 
                  class="flex-1 bg-surface-1 border border-primary text-primary font-button text-button py-sm rounded-lg hover:bg-surface-container-lowest transition-colors"
                  @click="approveDraft(collab.creator, false)"
                  :disabled="actioning"
                >
                  Reject &amp; Request Edits
                </button>
              </div>

              <!-- 3. AI_VERIFICATION_PENDING: Trigger AI Oracle -->
              <button 
                v-if="collab.status === 'AI_VERIFICATION_PENDING'"
                class="w-full bg-fin-orange text-white font-button text-button py-sm rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-sm shadow-sm"
                @click="verifyLivePost(collab.creator)"
                :disabled="actioning"
              >
                <span class="material-symbols-outlined text-[18px]">memory</span>
                Verify Live Post via AI Oracle
              </button>

              <!-- 4. RETENTION_MONITORING: Execute Payout -->
              <button 
                v-if="collab.status === 'RETENTION_MONITORING'"
                class="w-full bg-report-green text-on-primary font-button text-button py-sm rounded-lg hover:opacity-90 transition-opacity flex items-center justify-center gap-sm shadow-sm"
                @click="verifyRetention(collab.creator)"
                :disabled="actioning"
              >
                <span class="material-symbols-outlined text-[18px]">lock_open</span>
                Execute Retention Payout
              </button>

              <!-- 5. Cancel slot option if not complete/cancelled -->
              <button 
                v-if="collab.status !== 'FINALIZED' && collab.status !== 'COMPLETED' && collab.status !== 'CANCELLED' && collab.status !== 'BREACHED'"
                class="text-caption text-ink-subtle hover:text-error transition-colors text-right mt-xxs self-end"
                @click="cancelCollab(collab.creator)"
                :disabled="actioning"
              >
                Cancel Collaboration Slot
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- AI Consensus Audit Logs (Timeline) -->
      <section class="space-y-md bg-canvas border border-hairline rounded-xl p-lg md:p-xl">
        <div class="flex items-center gap-sm mb-lg">
          <span class="material-symbols-outlined text-fin-orange">verified_user</span>
          <h2 class="font-subhead text-subhead text-primary">AI Consensus Audit Log</h2>
        </div>
        
        <div class="relative border-l border-hairline ml-sm md:ml-md space-y-xl pb-md min-h-[100px]">
          <div v-if="parseAllHistory().length === 0" class="text-ink-subtle text-caption py-md pl-md">
            No audit logs have been recorded yet. Audit logs populate dynamically as creators submit milestones for validation.
          </div>
          
          <!-- Unified timeline events -->
          <div 
            v-for="(event, idx) in parseAllHistory()" 
            :key="idx" 
            class="relative pl-xl"
          >
            <div 
              class="absolute w-3 h-3 rounded-full -left-[6.5px] top-1.5 shadow-[0_0_0_4px_#fdf8f8]"
              :class="event.status === 'APPROVED' ? 'bg-report-green' : 'bg-error'"
            ></div>
            
            <div class="flex flex-col sm:flex-row sm:items-baseline gap-xs sm:gap-md mb-xs">
              <h4 class="font-body text-body font-medium text-primary">
                Consensus Reached: {{ event.status }} (Creator: @{{ getTwitterHandle(event.creator) }})
              </h4>
              <span class="font-mono text-mono text-ink-subtle">{{ formatTime(event.timestamp) }}</span>
            </div>
            
            <p class="font-body text-body-sm text-ink-muted mb-sm">
              Oracle network consensus evaluation completed: {{ event.reason }}
            </p>
            
            <div class="inline-flex gap-xs bg-surface-container-highest px-sm py-xs rounded border border-hairline">
              <span class="font-mono text-[11px] text-ink-subtle">Node 1: {{ event.status === 'APPROVED' ? 'PASS' : 'FAIL' }}</span>
              <span class="font-mono text-[11px] text-ink-subtle border-l border-hairline pl-xs">Node 2: {{ event.status === 'APPROVED' ? 'PASS' : 'FAIL' }}</span>
              <span class="font-mono text-[11px] text-ink-subtle border-l border-hairline pl-xs">Node 3: {{ event.status === 'APPROVED' ? 'PASS' : 'FAIL' }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- CREATOR / GUEST VIEW (Two column layout) -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-12 gap-lg items-start">
      <!-- Left Column: Primary Content (Active Work Area) -->
      <div class="lg:col-span-8 flex flex-col gap-lg">
        
        <!-- Creator Interaction Card (Active Milestone) -->
        <section v-if="myCollaboration" class="bg-surface-container-lowest border border-hairline rounded-xl p-lg md:p-xl shadow-sm relative overflow-hidden group">
          <div class="flex justify-between items-center mb-xl">
            <h2 class="font-headline text-headline text-primary tracking-tight">Active Milestone</h2>
            <span class="bg-surface-container-low border border-hairline text-ink-muted font-mono text-mono px-md py-sm rounded-lg uppercase tracking-wide">
              {{ myCollaboration.status }}
            </span>
          </div>

          <!-- Stepper Visual -->
          <div class="flex items-center w-full mb-xxl relative px-md">
            <!-- Step 1: Funded -->
            <div class="flex flex-col items-center relative flex-1 text-center">
              <div class="w-8 h-8 rounded-full bg-report-green text-on-primary flex items-center justify-center z-10 shadow-sm">
                <span class="material-symbols-outlined text-[18px]">check</span>
              </div>
              <span class="font-body text-[13px] text-primary mt-sm font-medium">Funded</span>
              <span class="font-caption text-[11px] text-ink-subtle">Completed</span>
              <div class="absolute top-4 left-1/2 w-full h-[2px] bg-report-green/30 -z-0"></div>
            </div>

            <!-- Step 2: Draft -->
            <div class="flex flex-col items-center relative flex-1 text-center">
              <div 
                class="w-8 h-8 rounded-full flex items-center justify-center z-10 shadow-sm"
                :class="myCollaboration.status !== 'WAITING_ESCROW' && myCollaboration.status !== 'DRAFT_SUBMISSION_OPEN' ? 'bg-report-green text-on-primary' : 'bg-surface-bright border border-hairline text-outline'"
              >
                <span v-if="myCollaboration.status !== 'WAITING_ESCROW' && myCollaboration.status !== 'DRAFT_SUBMISSION_OPEN'" class="material-symbols-outlined text-[18px]">check</span>
                <span v-else class="font-mono text-xs">2</span>
              </div>
              <span class="font-body text-[13px] text-primary mt-sm font-medium">Draft</span>
              <span class="font-caption text-[11px] text-ink-subtle">
                {{ myCollaboration.status === 'AWAITING_DRAFT_APPROVAL' ? 'Pending' : (myCollaboration.status === 'DRAFT_SUBMISSION_OPEN' ? 'Active' : 'Completed') }}
              </span>
              <div class="absolute top-4 left-1/2 w-full h-[2px] bg-hairline -z-0"></div>
            </div>

            <!-- Step 3: Publish -->
            <div class="flex flex-col items-center relative flex-1 text-center">
              <div 
                class="w-10 h-10 -mt-1 rounded-xl flex items-center justify-center z-10 shadow-md"
                :class="myCollaboration.status === 'AUTHORIZED_TO_PUBLISH' || myCollaboration.status === 'AI_VERIFICATION_PENDING' ? 'bg-fin-orange text-on-primary ring-4 ring-fin-orange/10' : (myCollaboration.status === 'RETENTION_MONITORING' || myCollaboration.status === 'FINALIZED' ? 'bg-report-green text-on-primary' : 'bg-surface-bright border border-hairline text-outline')"
              >
                <span v-if="myCollaboration.status === 'RETENTION_MONITORING' || myCollaboration.status === 'FINALIZED'" class="material-symbols-outlined text-[18px]">check</span>
                <span v-else class="material-symbols-outlined text-[24px]">send</span>
              </div>
              <span class="font-body text-[13px] text-primary mt-sm font-bold">Publish</span>
              <span class="font-caption text-[11px] text-fin-orange font-medium">
                {{ myCollaboration.status === 'AUTHORIZED_TO_PUBLISH' || myCollaboration.status === 'AI_VERIFICATION_PENDING' ? 'Awaiting Action' : 'Pending' }}
              </span>
              <div class="absolute top-4 left-1/2 w-full h-[2px] bg-hairline -z-0"></div>
            </div>

            <!-- Step 4: Retention -->
            <div class="flex flex-col items-center relative flex-1 text-center">
              <div 
                class="w-8 h-8 rounded-full z-10 flex items-center justify-center shadow-sm"
                :class="myCollaboration.status === 'FINALIZED' ? 'bg-report-green text-on-primary' : (myCollaboration.status === 'RETENTION_MONITORING' ? 'bg-fin-orange text-on-primary ring-4 ring-fin-orange/10' : 'bg-surface-bright border border-hairline text-outline')"
              >
                <span v-if="myCollaboration.status === 'FINALIZED'" class="material-symbols-outlined text-[18px]">check</span>
                <span v-else-if="myCollaboration.status === 'RETENTION_MONITORING'" class="material-symbols-outlined text-[18px]">schedule</span>
              </div>
              <span class="font-body text-[13px] text-ink-muted mt-sm">Retention</span>
              <span class="font-caption text-[11px] text-ink-subtle">
                {{ myCollaboration.status === 'RETENTION_MONITORING' ? 'Monitoring' : (myCollaboration.status === 'FINALIZED' ? 'Done' : 'Locked') }}
              </span>
            </div>
          </div>

          <!-- Dynamic Panel based on collaboration status -->
          <div class="bg-surface-bright border border-hairline rounded-xl p-lg md:p-xl flex flex-col gap-lg shadow-sm">
            
            <!-- WAITING_ESCROW -->
            <div v-if="myCollaboration.status === 'WAITING_ESCROW'" class="flex flex-col sm:flex-row items-start sm:items-center gap-md">
              <div class="flex items-center justify-center w-12 h-12 rounded-2xl bg-surface-container border border-hairline flex-shrink-0">
                <span class="material-symbols-outlined text-[28px] text-ink-subtle">hourglass_empty</span>
              </div>
              <div>
                <h3 class="font-headline text-subhead text-primary font-medium tracking-tight">Waiting for Escrow funding</h3>
                <p class="font-body text-body text-ink-subtle">The advertiser has not funded the escrow contract budget for your slot yet.</p>
              </div>
            </div>

            <!-- DRAFT_SUBMISSION_OPEN -->
            <div v-else-if="myCollaboration.status === 'DRAFT_SUBMISSION_OPEN'">
              <div class="flex flex-col sm:flex-row items-start sm:items-center gap-md mb-sm">
                <div class="flex items-center justify-center w-12 h-12 rounded-2xl bg-fin-orange/10 border border-fin-orange/20 flex-shrink-0">
                  <span class="material-symbols-outlined text-[28px] text-fin-orange">edit_document</span>
                </div>
                <div>
                  <h3 class="font-headline text-subhead text-primary font-medium tracking-tight">Submit Content Draft</h3>
                  <p class="font-body text-body text-ink-subtle">Enter your draft text matching all keywords and hashtag constraints.</p>
                </div>
              </div>
              <form @submit.prevent="submitDraft" class="flex flex-col gap-sm">
                <textarea 
                  class="bg-surface-container-lowest border border-hairline rounded-xl px-md md:px-lg py-md font-body text-body focus:outline-none focus:border-fin-orange focus:ring-1 focus:ring-fin-orange transition-shadow placeholder-outline-variant shadow-inner min-h-[120px]" 
                  v-model="creatorDraft" 
                  placeholder="Bobby is using GenLayer for decentralized AI escrows! #genlayer #web3" 
                  required
                  :disabled="actioning"
                  id="input-creator-draft"
                ></textarea>
                <button 
                  type="submit"
                  class="w-full sm:w-auto bg-fin-orange text-on-primary font-button text-body-lg px-xl py-md rounded-xl flex items-center justify-center gap-sm hover:opacity-90 transition-opacity shadow-sm sm:self-end"
                  :disabled="actioning"
                  id="btn-submit-draft"
                >
                  <span class="material-symbols-outlined text-[20px]">send</span>
                  Submit Draft for Review
                </button>
              </form>
            </div>

            <!-- AWAITING_DRAFT_APPROVAL -->
            <div v-else-if="myCollaboration.status === 'AWAITING_DRAFT_APPROVAL'">
              <div class="flex items-center gap-lg">
                <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-surface-container border border-hairline animate-pulse">
                  <span class="material-symbols-outlined text-[32px] text-ink-subtle">schedule</span>
                </div>
                <div>
                  <h3 class="font-headline text-subhead text-primary font-medium tracking-tight">Draft Submitted!</h3>
                  <p class="font-body text-body text-ink-subtle">Your draft is currently undergoing advertiser review. We will notify you once approved.</p>
                </div>
              </div>
              <div class="bg-surface-container-low border border-hairline rounded-xl p-md font-mono text-[13px] text-ink-muted">
                {{ myCollaboration.draft_text }}
              </div>
            </div>

            <!-- AUTHORIZED_TO_PUBLISH -->
            <div v-else-if="myCollaboration.status === 'AUTHORIZED_TO_PUBLISH' || myCollaboration.status === 'AI_VERIFICATION_PENDING'">
              <div class="flex items-center gap-lg mb-sm">
                <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-fin-orange/10 border border-fin-orange/20">
                  <span class="material-symbols-outlined text-[32px] text-fin-orange">verified</span>
                </div>
                <div>
                  <h3 class="font-headline text-subhead text-fin-orange font-medium tracking-tight">DRAFT APPROVED!</h3>
                  <p class="font-body text-body text-primary">Your content meets all AI requirements.</p>
                </div>
              </div>
              <div class="flex flex-col gap-sm">
                <p class="font-body text-body-lg text-ink-subtle mb-md">
                  Please publish your approved content to Twitter and submit the live URL below to initiate the AI verification process.
                </p>
                <div class="bg-surface-container-low border border-hairline rounded-xl p-md font-mono text-[13px] text-ink-muted mb-md">
                  <strong>Approved Text:</strong><br/>
                  {{ myCollaboration.draft_text }}
                </div>
                
                <form @submit.prevent="submitLivePost" class="flex flex-col gap-sm">
                  <label class="font-eyebrow text-eyebrow text-primary" for="post-url">Live Post URL</label>
                  <div class="flex flex-col sm:flex-row gap-md">
                    <input 
                      class="flex-grow bg-surface-container-lowest border border-hairline rounded-xl px-lg py-md font-body text-body focus:outline-none focus:border-fin-orange focus:ring-1 focus:ring-fin-orange transition-shadow placeholder-outline-variant shadow-inner" 
                      id="post-url" 
                      v-model="creatorLiveUrl"
                      placeholder="https://twitter.com/..." 
                      type="url"
                      required
                      :disabled="actioning || myCollaboration.status === 'AI_VERIFICATION_PENDING'"
                    />
                    <button 
                      type="submit"
                      class="bg-fin-orange text-on-primary font-button text-body-lg px-xl py-md rounded-xl flex items-center justify-center gap-sm hover:opacity-90 transition-opacity shadow-sm whitespace-nowrap"
                      :disabled="actioning || myCollaboration.status === 'AI_VERIFICATION_PENDING'"
                      id="btn-submit-live-post"
                    >
                      <span class="material-symbols-outlined text-[20px]">psychology</span>
                      Verify Live Post
                    </button>
                  </div>
                </form>
                
                <!-- Trigger Verification Node Directly -->
                <div v-if="myCollaboration.status === 'AI_VERIFICATION_PENDING'" class="mt-md p-md bg-surface-container border border-hairline rounded-xl flex justify-between items-center gap-md">
                  <div>
                    <span class="font-body text-body-sm font-bold text-primary block">AI Verification Trigger</span>
                    <span class="font-caption text-caption text-ink-subtle block">The post is currently in AI verification. You can manually run nodes to accelerate consensus.</span>
                  </div>
                  <button 
                    class="bg-primary text-on-primary px-md py-sm rounded font-button text-button hover:opacity-90 transition-opacity flex items-center gap-xs"
                    @click="verifyLivePost(account.address)"
                    :disabled="actioning"
                    id="btn-creator-trigger-verify"
                  >
                    <span class="material-symbols-outlined text-[16px]">bolt</span>
                    Accelerate AI
                  </button>
                </div>

                <p class="font-caption text-caption text-ink-muted mt-sm flex items-center gap-xs">
                  <span class="material-symbols-outlined text-[14px]">info</span>
                  The AI node will verify the live post matches the approved draft and contains the required metrics tracking.
                </p>
              </div>
            </div>

            <!-- RETENTION_MONITORING -->
            <div v-else-if="myCollaboration.status === 'RETENTION_MONITORING'">
              <div class="flex items-center gap-lg mb-sm">
                <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-report-green/10 border border-report-green/20">
                  <span class="material-symbols-outlined text-[32px] text-report-green">verified_user</span>
                </div>
                <div>
                  <h3 class="font-headline text-subhead text-report-green font-medium tracking-tight">LIVE POST VERIFIED!</h3>
                  <p class="font-body text-body text-primary">Initial milestone payments successfully released!</p>
                </div>
              </div>
              <div class="flex flex-col gap-sm">
                <p class="font-body text-body-lg text-ink-subtle">
                  Your live post is currently in the **Retention Period** (monitoring duration: {{ campaign.retention_duration_seconds / 3600 }} hours). Ensure your post remains published and unmodified to trigger final contract payouts.
                </p>
                <div class="p-md bg-surface-container border border-hairline rounded-xl flex justify-between items-center gap-md">
                  <div>
                    <span class="font-body text-body-sm font-bold text-primary block">Check Post Retention</span>
                    <span class="font-caption text-caption text-ink-subtle block">Submit a check query to verify retention and release the final contract payouts.</span>
                  </div>
                  <button 
                    class="bg-report-green text-on-primary px-md py-sm rounded font-button text-button hover:opacity-90 transition-opacity flex items-center gap-xs"
                    @click="verifyRetention(account.address)"
                    :disabled="actioning"
                  >
                    <span class="material-symbols-outlined text-[16px]">lock_open</span>
                    Release Escrow
                  </button>
                </div>
              </div>
            </div>

            <!-- FINALIZED -->
            <div v-else-if="myCollaboration.status === 'FINALIZED'">
              <div class="flex items-center gap-lg">
                <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-report-green/10 border border-report-green/20">
                  <span class="material-symbols-outlined text-[32px] text-report-green">emoji_events</span>
                </div>
                <div>
                  <h3 class="font-headline text-subhead text-report-green font-medium tracking-tight">Escrow Completed!</h3>
                  <p class="font-body text-body text-ink-subtle">All payments have been fully released from the smart contract escrow. Thank you for your work!</p>
                </div>
              </div>
            </div>

          </div>
        </section>

        <!-- Un-Collaborated Creator Apply Form -->
        <section v-else class="bg-surface-container-lowest border border-hairline rounded-xl p-lg md:p-xl shadow-sm text-left">
          <div v-if="myApplication">
            <h3 class="font-headline text-headline text-primary tracking-tight mb-md">My Application Status</h3>
            <div class="bg-surface-container-low border border-hairline rounded-xl p-lg flex justify-between items-center mb-md">
              <div>
                <span class="font-body text-body-sm font-bold text-primary block">@{{ myApplication.twitter_handle }}</span>
                <span class="font-caption text-caption text-ink-subtle block mt-xxs">Proposal: "{{ myApplication.proposal_message }}"</span>
              </div>
              <span class="px-md py-sm bg-surface-bright border border-hairline text-ink-muted font-mono text-xs rounded-xl uppercase font-bold">
                PENDING APPROVAL
              </span>
            </div>
          </div>
          <div v-else-if="isExpired">
            <h2 class="font-headline text-headline text-primary tracking-tight mb-md">Apply to Campaign</h2>
            <div class="bg-error-container/20 border border-error-container/30 rounded-xl p-lg flex flex-col items-center text-center gap-sm">
              <span class="material-symbols-outlined text-[40px] text-error">event_busy</span>
              <p class="font-headline text-subhead text-error font-medium">Applications Closed</p>
              <p class="font-body text-body-sm text-ink-subtle">
                This campaign has passed its posting deadline ({{ formatDate(campaign.posting_deadline).split(',')[0] }}) and is no longer accepting new applications.
              </p>
            </div>
          </div>
          <div v-else>
            <h2 class="font-headline text-headline text-primary tracking-tight mb-md">Apply to Campaign</h2>
            <form @submit.prevent="apply" class="flex flex-col gap-md">
              <div class="flex flex-col gap-xxs">
                <label class="font-eyebrow text-eyebrow text-primary" for="apply-handle">Twitter Handle</label>
                <input 
                  class="bg-surface-container-lowest border border-hairline rounded-xl px-lg py-md font-body text-body focus:outline-none focus:border-fin-orange focus:ring-1 focus:ring-fin-orange transition-shadow placeholder-outline-variant shadow-inner" 
                  id="apply-handle" 
                  v-model="applyForm.twitterHandle"
                  placeholder="e.g. your_twitter_handle" 
                  type="text"
                  required
                />
              </div>
              <div class="flex flex-col gap-xxs">
                <label class="font-eyebrow text-eyebrow text-primary" for="apply-proposal">Proposal Details</label>
                <textarea 
                  class="bg-surface-container-lowest border border-hairline rounded-xl px-lg py-md font-body text-body focus:outline-none focus:border-fin-orange focus:ring-1 focus:ring-fin-orange transition-shadow placeholder-outline-variant shadow-inner min-h-[100px]" 
                  id="apply-proposal" 
                  v-model="applyForm.proposalMessage"
                  placeholder="Briefly pitch why you are the ideal fit for this sponsorship..." 
                  required
                ></textarea>
              </div>
              <button 
                type="submit" 
                class="bg-fin-orange text-white font-button text-body-lg px-xl py-md rounded-xl flex items-center justify-center gap-sm hover:opacity-90 transition-opacity shadow-sm self-end"
                :disabled="actioning"
                id="btn-apply-submit"
              >
                Submit Application
              </button>
            </form>
          </div>
        </section>

      </div>

      <!-- Right Column: Sidebar (Context & Logs) -->
      <div class="lg:col-span-4 flex flex-col gap-lg lg:sticky lg:top-[88px]">
        
        <!-- Campaign Brief Card -->
        <section class="bg-surface-1 border border-hairline rounded-xl p-xl shadow-sm text-left">
          <div class="flex items-center justify-between mb-md text-ink-subtle">
            <div class="flex items-center gap-sm">
              <span class="material-symbols-outlined text-[18px]">tag</span>
              <span class="font-eyebrow text-eyebrow uppercase tracking-wider">{{ campaign.platform ? campaign.platform.toUpperCase() : 'Twitter' }} Promotion</span>
            </div>
            <span v-if="isExpired" class="px-2 py-0.5 rounded-full bg-error-container/10 border border-error-container/30 font-mono text-[10px] text-error uppercase font-bold">
              Expired
            </span>
          </div>

          <h1 class="font-headline text-headline text-primary mb-md leading-tight tracking-[-0.5px]">
            {{ campaign.title }}
          </h1>

          <div class="flex items-center gap-sm font-mono text-mono text-ink-subtle mb-xl bg-surface-container-low w-fit px-sm py-xs rounded border border-hairline">
            <span class="text-[11px]">Advertiser:</span>
            <span class="text-primary font-medium">{{ campaign.advertiser.slice(0, 6) }}...{{ campaign.advertiser.slice(-4) }}</span>
            <span class="material-symbols-outlined text-[14px] cursor-pointer hover:text-primary" @click="navigator.clipboard.writeText(campaign.advertiser)">content_copy</span>
          </div>

          <div class="bg-surface-2/40 rounded-xl p-lg border border-hairline mb-xl">
            <div class="font-eyebrow text-caption text-ink-muted uppercase mb-xs tracking-wider">Escrow Budget</div>
            <div class="font-display-md text-display-md text-primary tracking-tight leading-none">
              {{ formatGen(campaign.atto_budget_per_creator) }} 
              <span class="font-headline text-headline text-ink-subtle align-bottom ml-xs">GEN</span>
            </div>
          </div>

          <div class="flex flex-col gap-lg">
            <div class="flex flex-col gap-sm">
              <div class="font-body text-body-sm text-ink-subtle font-medium">Required Tags &amp; Keywords</div>
              <div class="flex flex-wrap gap-sm">
                <!-- Tags -->
                <span v-for="tag in parseArray(campaign.required_hashtags)" :key="tag" class="px-md py-sm border border-hairline rounded-full font-body text-[12px] text-primary bg-surface-bright shadow-sm">
                  {{ tag }}
                </span>
                <!-- Keywords -->
                <span v-for="kw in parseArray(campaign.required_keywords)" :key="kw" class="px-md py-sm border border-hairline rounded-full font-body text-[12px] text-primary bg-surface-bright shadow-sm">
                  {{ kw }}
                </span>
                <span v-if="parseArray(campaign.required_hashtags).length === 0 && parseArray(campaign.required_keywords).length === 0" class="text-ink-subtle text-caption">
                  None
                </span>
              </div>
            </div>

            <div class="space-y-sm pt-lg border-t border-hairline">
              <div class="flex items-center gap-sm text-ink-muted">
                <span class="material-symbols-outlined text-[20px] text-primary">calendar_today</span>
                <span class="font-body text-body-sm">Deadline: <strong class="text-primary font-medium">{{ formatDate(campaign.posting_deadline).split(',')[0] }}</strong></span>
              </div>
              <div class="flex items-center gap-sm text-ink-muted">
                <span class="material-symbols-outlined text-[20px] text-primary">schedule</span>
                <span class="font-body text-body-sm">Duration: <strong class="text-primary font-medium">{{ campaign.retention_duration_seconds / 3600 }} Hours</strong></span>
              </div>
              <div class="flex items-center gap-sm text-ink-muted">
                <span class="material-symbols-outlined text-[20px] text-primary">group</span>
                <span class="font-body text-body-sm">Slots: <strong class="text-primary font-medium">{{ campaign.active_creators_count }} / {{ campaign.max_creators }} Filled</strong></span>
              </div>
            </div>
          </div>
        </section>

        <!-- Audit Logs Section -->
        <section class="bg-surface-1 border border-hairline rounded-xl p-xl shadow-sm text-left">
          <div class="flex items-center justify-between mb-xl">
            <h2 class="font-card-title text-card-title text-primary">Audit Logs</h2>
            <span class="material-symbols-outlined text-ink-subtle">history</span>
          </div>

          <!-- Logs listing -->
          <div class="relative border-l border-hairline ml-sm space-y-xl pl-lg min-h-[100px]">
            
            <div v-if="!myCollaboration && !isAdvertiser" class="text-ink-subtle text-caption py-md">
              No audit logs recorded for your session. Logs will populate once you begin collaboration milestones.
            </div>

            <div v-else-if="myCollaboration && parseHistory(myCollaboration.verdict_history_json).length === 0" class="text-ink-subtle text-caption py-md">
              Awaiting milestone evaluations. Audit details will post here once drafts or URLs are validated by AI consensus.
            </div>

            <div v-else-if="isAdvertiser && collaborations.length === 0" class="text-ink-subtle text-caption py-md">
              No active slots to audit.
            </div>

            <!-- Timeline nodes -->
            <div 
              v-for="(event, idx) in (isAdvertiser ? parseHistory(collaborations[0]?.verdict_history_json) : parseHistory(myCollaboration?.verdict_history_json))" 
              :key="idx" 
              class="relative"
            >
              <div 
                class="absolute -left-[29px] top-1 w-3 h-3 rounded-full ring-4 ring-surface-1"
                :class="event.status === 'APPROVED' ? 'bg-report-green' : 'bg-error'"
              ></div>
              <div class="font-caption text-caption text-ink-muted mb-xxs">{{ formatTime(event.timestamp) }}</div>
              <div class="font-body text-body-sm font-medium text-primary mb-sm">
                {{ formatEventType(event.type) }} - {{ event.status }}
              </div>
              <div class="bg-report-green/5 border border-report-green/20 rounded-lg p-sm font-mono text-mono text-ink-subtle text-[11px] leading-relaxed break-words shadow-inner">
                &gt; SYSTEM: AI Node Verification<br/>
                &gt; STATUS: {{ event.status }}<br/>
                &gt; REASONING: {{ event.reason }}
              </div>
            </div>

          </div>
        </section>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { CheckCircle, XCircle } from 'lucide-vue-next';

const props = defineProps({
  campaign: Object,
  account: Object,
  escrow: Object
});

const emit = defineEmits(['refresh']);

const applications = ref([]);
const collaborations = ref([]);
const actioning = ref(false);

const applyForm = reactive({
  twitterHandle: '',
  proposalMessage: ''
});

const creatorDraft = ref('');
const creatorLiveUrl = ref('');

// Computed fields
const isAdvertiser = computed(() => {
  if (!props.account) return false;
  return props.campaign.advertiser.toLowerCase() === props.account.address.toLowerCase();
});

const myApplication = computed(() => {
  if (!props.account) return null;
  return applications.value.find(a => a.creator.toLowerCase() === props.account.address.toLowerCase());
});

const myCollaboration = computed(() => {
  if (!props.account) return null;
  return collaborations.value.find(c => c.creator.toLowerCase() === props.account.address.toLowerCase());
});

const isExpired = computed(() => {
  if (!props.campaign || !props.campaign.posting_deadline) return false;
  return new Date() > new Date(props.campaign.posting_deadline);
});

// Parse custom storage arrays/JSON formats
function parseArray(val) {
  if (!val) return [];
  if (Array.isArray(val)) return val;
  try {
    const parsed = JSON.parse(val);
    if (Array.isArray(parsed)) return parsed;
  } catch (e) {}
  if (typeof val === 'string') {
    return val.split(/[,\s]+/).map(s => s.trim()).filter(Boolean);
  }
  return [];
}

function formatGen(atto) {
  if (!atto) return '0';
  return (Number(atto) / 1e18).toFixed(2);
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString();
}

// Actions
async function loadSubData() {
  if (!props.escrow || !props.campaign) return;
  try {
    applications.value = await props.escrow.getApplications(props.campaign.id);
    collaborations.value = await props.escrow.getCollaborations(props.campaign.id);

    // Pre-populate creator forms if collaborating
    const myCollab = myCollaboration.value;
    if (myCollab) {
      creatorDraft.value = myCollab.draft_text || '';
      creatorLiveUrl.value = myCollab.live_tweet_url || '';
    }
  } catch (err) {
    console.error('Load details subdata failed:', err);
  }
}

// Toast helper for asynchronous transactions
async function runWithToast(title, actionPromiseCreator, successTitle, successMsg, errorTitle) {
  if (actioning.value) return;
  actioning.value = true;
  
  let toastId = null;
  if (window.marketplaceToast) {
    toastId = window.marketplaceToast.add({
      title: title,
      message: 'Please confirm the transaction in MetaMask.',
      type: 'progress',
      steps: ['Submit Transaction', 'Consensus Processing', 'Finalized'],
      currentStep: 0,
      duration: 0
    });
  }
  
  try {
    const onTxHash = (txHash) => {
      if (toastId && window.marketplaceToast) {
        window.marketplaceToast.update(toastId, {
          currentStep: 1,
          message: `Transaction submitted! Hash: ${txHash.slice(0, 10)}... Awaiting AI consensus...`
        });
      }
    };
    
    await actionPromiseCreator(onTxHash);
    
    await loadSubData();
    emit('refresh');
    
    if (toastId && window.marketplaceToast) {
      window.marketplaceToast.update(toastId, {
        type: 'success',
        title: successTitle,
        message: successMsg,
        currentStep: 3,
        duration: 5000
      });
    }
  } catch (err) {
    console.error(err);
    if (toastId && window.marketplaceToast) {
      window.marketplaceToast.update(toastId, {
        type: 'error',
        title: errorTitle || 'Transaction Failed',
        message: err.message || err,
        duration: 6000
      });
    } else {
      alert(`${errorTitle || 'Transaction Failed'}: ${err.message || err}`);
    }
  } finally {
    actioning.value = false;
  }
}

async function apply() {
  await runWithToast(
    'Submitting Application',
    (onTxHash) => props.escrow.applyToCampaign(props.campaign.id, applyForm.twitterHandle, applyForm.proposalMessage, onTxHash),
    'Application Submitted!',
    'Your application has been registered successfully.',
    'Application Failed'
  );
}

async function approveCreator(creatorAddr) {
  await runWithToast(
    'Approving Creator',
    (onTxHash) => props.escrow.approveCreator(props.campaign.id, creatorAddr, onTxHash),
    'Creator Approved!',
    'Creator has been approved for the campaign.',
    'Approval Failed'
  );
}

async function fundEscrow(creatorAddr) {
  const amount = props.campaign.atto_budget_per_creator;
  await runWithToast(
    'Funding Escrow',
    (onTxHash) => props.escrow.depositEscrow(props.campaign.id, creatorAddr, amount, onTxHash),
    'Escrow Funded!',
    'Budget has been successfully deposited in escrow.',
    'Funding Failed'
  );
}

async function submitDraft() {
  await runWithToast(
    'Submitting Draft',
    (onTxHash) => props.escrow.submitDraft(props.campaign.id, creatorDraft.value, onTxHash),
    'Draft Submitted!',
    'Your draft has been submitted for advertiser approval.',
    'Draft Submission Failed'
  );
}

async function approveDraft(creatorAddr, approved) {
  const title = approved ? 'Approving Draft' : 'Rejecting Draft';
  const successTitle = approved ? 'Draft Approved!' : 'Draft Rejected';
  const successMsg = approved ? 'Creator is now authorized to publish.' : 'Draft returned to creator for modifications.';
  await runWithToast(
    title,
    (onTxHash) => props.escrow.approveDraft(props.campaign.id, creatorAddr, approved, onTxHash),
    successTitle,
    successMsg,
    'Draft Approval Failed'
  );
}

async function submitLivePost() {
  await runWithToast(
    'Submitting Live Post',
    (onTxHash) => props.escrow.submitLivePost(props.campaign.id, creatorLiveUrl.value, onTxHash),
    'Live Post Submitted!',
    'Your live post url is now pending AI verification.',
    'Submission Failed'
  );
}

async function verifyLivePost(creatorAddr) {
  await runWithToast(
    'Verifying Live Post',
    (onTxHash) => props.escrow.verifyLivePost(props.campaign.id, creatorAddr, onTxHash),
    'Verification Completed!',
    'AI Consensus has completed verification of the live post.',
    'Verification Failed'
  );
}

async function verifyRetention(creatorAddr) {
  await runWithToast(
    'Checking Post Retention',
    (onTxHash) => props.escrow.verifyRetention(props.campaign.id, creatorAddr, onTxHash),
    'Retention Check Done!',
    'AI Consensus has completed the post retention validation.',
    'Retention Check Failed'
  );
}

async function cancelCollab(creatorAddr) {
  await runWithToast(
    'Cancelling Collaboration',
    (onTxHash) => props.escrow.cancelCollaboration(props.campaign.id, creatorAddr, onTxHash),
    'Collaboration Cancelled',
    'The collaboration was successfully cancelled and budget refunded.',
    'Cancellation Failed'
  );
}

function parseHistory(jsonStr) {
  if (!jsonStr) return [];
  try {
    const history = JSON.parse(jsonStr);
    if (Array.isArray(history)) {
      return history.slice().reverse(); // Show latest first
    }
  } catch (e) {
    console.error('Failed to parse verdict history:', e);
  }
  return [];
}

function formatEventType(type) {
  if (type === 'draft') return 'Content Draft';
  if (type === 'live_post') return 'AI Live Verification';
  if (type === 'retention') return 'AI Retention Check';
  return type.toUpperCase();
}

function formatTime(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  } catch (e) {
    return isoStr;
  }
}

function getTwitterHandle(creatorAddr) {
  if (!creatorAddr) return '';
  const app = applications.value.find(a => a.creator.toLowerCase() === creatorAddr.toLowerCase());
  return app ? app.twitter_handle : `${creatorAddr.slice(0, 6)}...${creatorAddr.slice(-4)}`;
}

function parseAllHistory() {
  const all = [];
  collaborations.value.forEach(c => {
    const history = parseHistory(c.verdict_history_json);
    history.forEach(h => {
      all.push({
        ...h,
        creator: c.creator
      });
    });
  });
  return all.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

function simulateAdvertiserAction(actionName) {
  if (window.marketplaceToast) {
    window.marketplaceToast.add({
      title: 'Action Restrained',
      message: `${actionName} is currently governed by on-chain AI consensus. Direct manual state modification is disabled in this network phase.`,
      type: 'warning',
      duration: 5000
    });
  } else {
    alert(`${actionName} is governed by on-chain AI consensus.`);
  }
}

onMounted(() => {
  loadSubData();
});
</script>

<style scoped>
.campaign-detail {
  width: 100%;
}

.form-stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.form-group {
  display: flex;
  flex-direction: column;
}

/* Timeline component styling */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-left: 2px solid var(--color-hairline);
  padding-left: 16px;
  margin-left: 8px;
  margin-top: var(--space-sm);
}

.timeline-item {
  position: relative;
}

.timeline-icon {
  position: absolute;
  left: -24px;
  top: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border: 1px solid var(--color-hairline);
}

.bg-success {
  background: var(--color-brand-green);
  color: var(--color-primary);
  border-color: var(--color-brand-green-deep);
}

.bg-error {
  background: var(--color-brand-error);
  color: var(--color-on-dark);
  border-color: var(--color-brand-error);
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink);
}

.timeline-time {
  font-size: 11px;
  color: var(--color-stone);
}

.timeline-desc {
  font-size: 12px;
  color: var(--color-steel);
  line-height: 1.4;
}
</style>
