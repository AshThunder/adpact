<template>
  <div class="modal-overlay fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 backdrop-blur-md p-0 sm:p-md" @click.self="$emit('close')">
    <div class="modal bg-canvas border border-hairline rounded-t-2xl sm:rounded-2xl max-w-3xl w-full p-md md:p-xl shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-xl">
        <h3 class="font-headline text-headline text-primary">Create Campaign</h3>
        <button class="text-ink-subtle hover:text-primary transition-colors p-xs flex items-center justify-center rounded-lg" @click="$emit('close')" id="btn-close-create-modal">
          <span class="material-symbols-outlined text-[24px]">close</span>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="submit" class="space-y-xl flex-1">
        <!-- Campaign Title -->
        <div class="flex flex-col">
          <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Campaign Title</label>
          <input 
            class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
            v-model="form.title" 
            placeholder="e.g. Web3 Gaming Platform Launch Promotion" 
            required 
            id="input-campaign-title" 
          />
        </div>

        <!-- Description -->
        <div class="flex flex-col">
          <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Description</label>
          <textarea 
            class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors min-h-[120px] resize-y" 
            v-model="form.description" 
            placeholder="Describe the campaign and draft requirements..." 
            required 
            id="input-campaign-description"
          ></textarea>
        </div>

        <!-- Platform Selection -->
        <div class="flex flex-col">
          <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Platform</label>
          <div class="flex flex-wrap gap-sm bg-surface-container p-1.5 rounded-xl border border-hairline w-full">
            <button
              v-for="p in platforms"
              :key="p"
              type="button"
              :disabled="p !== 'twitter'"
              class="px-5 py-2.5 rounded-lg font-button text-body-sm transition-all uppercase tracking-wider flex items-center gap-1.5"
              :class="form.platform === p ? 'bg-surface-1 text-primary shadow-sm border border-hairline font-medium' : (p !== 'twitter' ? 'text-ink-subtle/40 cursor-not-allowed opacity-50' : 'text-ink-subtle hover:text-primary')"
              @click="p === 'twitter' && (form.platform = p)"
            >
              {{ p === 'twitter' ? 'X / Twitter' : p }}
              <span v-if="p !== 'twitter'" class="text-[9px] bg-ink-subtle/10 px-1.5 py-0.5 rounded font-normal lowercase tracking-normal">Soon</span>
            </button>
          </div>
        </div>

        <!-- Budget & Slots -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Budget per Creator (GEN)</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              type="number" 
              step="0.01" 
              min="0.01" 
              v-model.number="form.budgetGen" 
              placeholder="500.0" 
              required 
              id="input-budget" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Amount deposited in escrow per slot</span>
          </div>
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Max Slots</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              type="number" 
              min="1" 
              v-model.number="form.maxCreators" 
              placeholder="5" 
              required 
              id="input-max-creators" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Total creators allowed to participate</span>
          </div>
        </div>

        <!-- Requirements -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Required Hashtags</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              v-model="form.hashtagsRaw" 
              placeholder="#genlayer, #web3" 
              id="input-hashtags" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Comma-separated</span>
          </div>
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Required Keywords</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              v-model="form.keywordsRaw" 
              placeholder="blockchain, intelligent" 
              id="input-keywords" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Comma-separated</span>
          </div>
        </div>

        <!-- Payout Distribution & Deadlines -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Posting Deadline</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              type="datetime-local" 
              v-model="form.postingDeadline" 
              required 
              id="input-deadline" 
            />
          </div>
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Post Retention (hours)</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              type="number" 
              min="1" 
              v-model.number="form.retentionHours" 
              placeholder="24" 
              required 
              id="input-retention" 
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-lg">
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Initial Payout %</label>
            <input 
              class="w-full bg-surface-1 border border-hairline rounded-xl px-5 py-4 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors" 
              type="number" 
              min="0" 
              max="100" 
              v-model.number="form.initialPct" 
              placeholder="30" 
              required 
              id="input-initial-pct" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Paid on successful live tweet verification</span>
          </div>
          <div class="flex flex-col">
            <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block mb-sm font-medium">Retention Payout %</label>
            <input 
              class="w-full bg-surface-2 border border-hairline rounded-xl px-5 py-4 font-body text-body text-ink-subtle opacity-75 cursor-not-allowed" 
              type="number" 
              :value="100 - form.initialPct" 
              disabled 
              id="input-retention-pct" 
            />
            <span class="text-body-sm text-ink-muted mt-2 font-body">Paid on post retention validation</span>
          </div>
        </div>

        <!-- Divider -->
        <hr class="border-t border-hairline my-md" />

        <!-- Actions -->
        <div class="flex flex-col-reverse sm:flex-row gap-md sm:justify-end items-stretch sm:items-center">
          <button 
            type="button" 
            class="font-button text-body bg-surface-1 border border-hairline text-primary px-6 py-3 rounded-xl hover:bg-surface-2 transition-colors" 
            @click="$emit('close')" 
            id="btn-cancel-create"
          >
            Cancel
          </button>
          
          <button 
            type="submit" 
            class="font-button text-body bg-primary text-on-primary px-8 py-3 rounded-xl flex items-center gap-2 hover:opacity-90 transition-opacity shadow-sm font-medium" 
            :disabled="submitting" 
            id="btn-submit-campaign"
          >
            <div v-if="submitting" class="spinner border-2 border-on-primary border-t-transparent w-4 h-4 rounded-full animate-spin"></div>
            <span v-else>Create Campaign</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

const emit = defineEmits(['close', 'created']);
const props = defineProps({ escrow: Object });

const platforms = ['twitter', 'youtube', 'newsletter'];
const submitting = ref(false);

const form = reactive({
  title: '',
  description: '',
  budgetGen: 1,
  maxCreators: 1,
  platform: 'twitter',
  hashtagsRaw: '',
  keywordsRaw: '',
  retentionHours: 24,
  postingDeadline: '',
  initialPct: 30,
});

async function submit() {
  if (submitting.value) return;

  // Guard: contract address must be set for the selected network
  if (!props.escrow || !props.escrow.contractAddress) {
    alert('No contract deployed on this network. Please switch to StudioNet or Bradbury in the network selector.');
    return;
  }

  submitting.value = true;

  try {
    const hashtags = form.hashtagsRaw.split(',').map(s => s.trim()).filter(Boolean);
    const keywords = form.keywordsRaw.split(',').map(s => s.trim()).filter(Boolean);
    const attoBudget = BigInt(Math.floor(form.budgetGen * 1e18));
    const deadlineISO = new Date(form.postingDeadline).toISOString();

    await props.escrow.createCampaign({
      title: form.title,
      description: form.description,
      attoBudgetPerCreator: attoBudget,
      maxCreators: form.maxCreators,
      platform: form.platform,
      requiredHashtags: hashtags,
      requiredKeywords: keywords,
      retentionDurationSeconds: form.retentionHours * 3600,
      postingDeadline: deadlineISO,
      paymentStructure: { initial: form.initialPct, retention: 100 - form.initialPct },
    });

    emit('created');
    emit('close');
  } catch (err) {
    console.error('Create campaign failed:', err);
    alert('Failed to create campaign: ' + (err.message || err));
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
/* Scoped styles kept minimal due to full Tailwind usage */
</style>
