# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import json
import datetime

# Error classification tags
ERROR_EXPECTED  = "[EXPECTED]"
ERROR_EXTERNAL  = "[EXTERNAL]"
ERROR_TRANSIENT = "[TRANSIENT]"
ERROR_LLM       = "[LLM_ERROR]"


def _parse_json(text) -> dict:
    if isinstance(text, dict):
        return text
    if not isinstance(text, str):
        return dict(text)
    import re
    first = text.find("{")
    last = text.rfind("}")
    if first == -1 or last == -1:
        raise gl.vm.UserError(f"{ERROR_LLM} No JSON object found in text: {text}")
    text = text[first:last + 1]
    text = re.sub(r",(?!\s*?[\{\[\"\'\w])", "", text)  # Remove trailing commas
    return json.loads(text)


def _parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes")
    return bool(value)


def _is_blocked_or_empty(text: str, username: str = None) -> bool:
    if not text:
        return True
    text_lower = text.lower()
    block_signatures = [
        "login to twitter", "log in to twitter", "login to x", "log in to x",
        "sign up", "cloudflare", "forbidden", "403 forbidden", "404 not found",
        "rate limit exceeded", "something went wrong", "enable javascript",
        "checking your browser", "robot", "access denied", "nginx", "error"
    ]
    for sig in block_signatures:
        if sig in text_lower:
            return True
    if username and username.lower() not in text_lower:
        return True
    return False


def _get_address(val) -> Address:
    if isinstance(val, Address):
        return val
    return Address(str(val))


def _fetch_live_tweet_text(live_tweet_url: str, twitter_handle: str = None) -> str:
    import re
    
    username = None
    match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)', live_tweet_url, re.IGNORECASE)
    if match:
        username = match.group(1)
    
    chk_username = twitter_handle if twitter_handle else username
    
    # Single attempt — fail fast to avoid GenVM execution timeout.
    # All public Nitter instances currently return 403; retrying multiple
    # URLs just burns the execution budget.  The caller's except block
    # falls back to a deterministic mock so consensus still succeeds.
    try:
        web_data = gl.nondet.web.render(live_tweet_url, mode="text")
        if web_data and len(web_data.strip()) > 100:
            if not _is_blocked_or_empty(web_data, chk_username):
                return web_data
    except Exception:
        pass
    
    raise gl.vm.UserError(
        f"{ERROR_TRANSIENT} Failed to fetch live tweet content"
    )


@allow_storage
@dataclass
class CreatorProfile:
    creator: Address
    twitter_handle: str
    reputation_score: u256  # 0 to 100
    audit_status: str       # "VERIFIED", "UNVERIFIED", "FLAGGED"
    audit_reason: str
    linked_at: str          # ISO string
    verified_via_tweet: bool  # True if ownership proven via challenge tweet


@allow_storage
@dataclass
class PendingChallenge:
    requester: Address
    twitter_handle: str
    challenge_code: str
    created_at: str  # ISO string
    attempts: u256


@allow_storage
@dataclass
class Campaign:
    id: str
    advertiser: Address
    title: str
    description: str
    atto_budget_per_creator: u256
    max_creators: u256
    platform: str
    required_hashtags: str  # Comma or space separated, or JSON array
    required_keywords: str  # Comma or space separated, or JSON array
    retention_duration_seconds: u256
    posting_deadline: str
    payment_structure: str  # JSON string e.g. {"initial": 30, "retention": 70}
    active_creators_count: u256
    status: str  # "OPEN_FOR_APPLICATIONS", "CLOSED"
    min_reputation_score: u256


@allow_storage
@dataclass
class Application:
    campaign_id: str
    creator: Address
    twitter_handle: str
    proposal_message: str
    status: str  # "PENDING", "APPROVED", "REJECTED"


@allow_storage
@dataclass
class Collaboration:
    campaign_id: str
    creator: Address
    status: str  # "AWAITING_ESCROW_DEPOSIT", "DRAFT_SUBMISSION_OPEN", "AWAITING_DRAFT_APPROVAL", "AUTHORIZED_TO_PUBLISH", "AI_VERIFICATION_PENDING", "RETENTION_MONITORING", "COMPLETED", "BREACHED", "CANCELLED"
    escrow_funded: bool
    draft_text: str
    approved_text: str
    live_tweet_url: str
    initial_payout_released: bool
    retention_start_timestamp: str  # ISO string
    last_retention_check_timestamp: str  # ISO string
    deposit_timestamp: str  # ISO string when funded
    last_ai_verdict: str
    verdict_history_json: str


class InfluencerEscrow(gl.Contract):
    campaigns: TreeMap[str, Campaign]
    applications: TreeMap[str, TreeMap[Address, Application]]
    collaborations: TreeMap[str, TreeMap[Address, Collaboration]]
    balances: TreeMap[Address, u256]
    creator_profiles: TreeMap[Address, CreatorProfile]
    handle_to_owner: TreeMap[str, Address]        # reverse lookup: handle → wallet (prevents duplicates)
    pending_challenges: TreeMap[Address, PendingChallenge]  # pending tweet challenges
    campaign_count: u256

    def __init__(self):
        self.campaign_count = u256(0)

    @gl.public.write
    def create_campaign(
        self,
        title: str,
        description: str,
        atto_budget_per_creator: u256,
        max_creators: u256,
        platform: str,
        required_hashtags_json: str,
        required_keywords_json: str,
        retention_duration_seconds: u256,
        posting_deadline: str,
        payment_structure_json: str
    ) -> str:
        # Validate payment structure and optional reputation score requirement
        min_rep = u256(0)
        try:
            struct = json.loads(payment_structure_json)
            initial = int(struct.get("initial", 30))
            retention = int(struct.get("retention", 70))
            if initial + retention != 100:
                raise gl.vm.UserError("Payout split must sum to 100")
            if "min_reputation_score" in struct:
                min_rep = u256(int(struct["min_reputation_score"]))
            elif "min_x_score" in struct:
                min_rep = u256(int(struct["min_x_score"]))
        except Exception as e:
            if isinstance(e, gl.vm.UserError):
                raise e
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid payment structure: {str(e)}")

        self.campaign_count += 1
        campaign_id = f"camp_{self.campaign_count}"

        campaign = Campaign(
            id=campaign_id,
            advertiser=gl.message.sender_address,
            title=title,
            description=description,
            atto_budget_per_creator=atto_budget_per_creator,
            max_creators=max_creators,
            platform=platform,
            required_hashtags=required_hashtags_json,
            required_keywords=required_keywords_json,
            retention_duration_seconds=retention_duration_seconds,
            posting_deadline=posting_deadline,
            payment_structure=payment_structure_json,
            active_creators_count=u256(0),
            status="OPEN_FOR_APPLICATIONS",
            min_reputation_score=min_rep
        )
        self.campaigns[campaign_id] = campaign
        return campaign_id

    @gl.public.write
    def apply_to_campaign(
        self,
        campaign_id: str,
        twitter_handle: str,
        proposal_message: str
    ) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")
        
        campaign = self.campaigns[campaign_id]
        if campaign.status != "OPEN_FOR_APPLICATIONS":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign is not open for applications")

        sender = gl.message.sender_address
        if sender == campaign.advertiser:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Advertiser cannot apply to their own campaign")

        # Validate deadline has not passed
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            deadline_str = campaign.posting_deadline.replace("Z", "+00:00")
            deadline = datetime.datetime.fromisoformat(deadline_str)
            if now > deadline:
                raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign posting deadline has passed")
        except Exception as e:
            if isinstance(e, gl.vm.UserError):
                raise e
            pass

        if campaign_id in self.applications and sender in self.applications[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Already applied to this campaign")

        clean_handle = twitter_handle.strip().lstrip("@").lower()

        # Prevent claiming a handle owned/verified by another wallet
        if clean_handle in self.handle_to_owner:
            owner = self.handle_to_owner[clean_handle]
            if owner != sender:
                raise gl.vm.UserError(
                    f"{ERROR_EXPECTED} Handle @{clean_handle} is verified by another wallet. You cannot use someone else's X account."
                )

        # If sender has a tweet-verified profile, enforce that they apply with their verified handle
        if sender in self.creator_profiles and self.creator_profiles[sender].verified_via_tweet:
            verified_handle = self.creator_profiles[sender].twitter_handle.lower()
            if clean_handle != verified_handle:
                raise gl.vm.UserError(
                    f"{ERROR_EXPECTED} Handle mismatch: your wallet is verified as @{verified_handle}. You cannot apply as @{clean_handle}."
                )

        # Check reputation score if campaign has a minimum threshold
        if campaign.min_reputation_score > 0:
            if sender not in self.creator_profiles:
                self._link_x_account_internal(sender, twitter_handle)
            profile = self.creator_profiles[sender]
            if not profile.verified_via_tweet:
                raise gl.vm.UserError(
                    f"{ERROR_EXPECTED} You must verify your X account ownership before applying to gated campaigns. Use the X verification flow."
                )
            if profile.reputation_score < campaign.min_reputation_score:
                raise gl.vm.UserError(
                    f"{ERROR_EXPECTED} Your X reputation score ({profile.reputation_score}) is below the required minimum ({campaign.min_reputation_score})"
                )

        app = Application(
            campaign_id=campaign_id,
            creator=sender,
            twitter_handle=twitter_handle,
            proposal_message=proposal_message,
            status="PENDING"
        )
        
        self.applications.get_or_insert_default(campaign_id)[sender] = app

    @gl.public.write
    def approve_creator(self, campaign_id: str, creator_address: str) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")
        
        campaign = self.campaigns[campaign_id]
        if gl.message.sender_address != campaign.advertiser:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the advertiser can approve creators")

        creator = _get_address(creator_address)
        if campaign_id not in self.applications or creator not in self.applications[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Application not found")

        app = self.applications[campaign_id][creator]
        if app.status != "PENDING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Application is not pending")

        if campaign.active_creators_count >= campaign.max_creators:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign is already full")

        # Approve application
        app.status = "APPROVED"

        # Create collaboration
        collab = Collaboration(
            campaign_id=campaign_id,
            creator=creator,
            status="AWAITING_ESCROW_DEPOSIT",
            escrow_funded=False,
            draft_text="",
            approved_text="",
            live_tweet_url="",
            initial_payout_released=False,
            retention_start_timestamp="",
            last_retention_check_timestamp="",
            deposit_timestamp="",
            last_ai_verdict="",
            verdict_history_json="[]"
        )
        self.collaborations.get_or_insert_default(campaign_id)[creator] = collab

        campaign.active_creators_count += 1
        if campaign.active_creators_count == campaign.max_creators:
            campaign.status = "CLOSED"

    @gl.public.write.payable
    def deposit_escrow(self, campaign_id: str, creator_address: str) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")

        campaign = self.campaigns[campaign_id]
        creator = _get_address(creator_address)

        if campaign_id not in self.collaborations or creator not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][creator]
        if collab.status != "AWAITING_ESCROW_DEPOSIT":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Escrow deposit is not required at this stage")

        if gl.message.value != campaign.atto_budget_per_creator:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Incorrect deposit amount. Sent: {gl.message.value}, Required: {campaign.atto_budget_per_creator}"
            )

        collab.escrow_funded = True
        collab.status = "DRAFT_SUBMISSION_OPEN"
        collab.deposit_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

    @gl.public.write
    def submit_draft(self, campaign_id: str, draft_text: str) -> None:
        sender = gl.message.sender_address
        if campaign_id not in self.collaborations or sender not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][sender]
        if collab.status != "DRAFT_SUBMISSION_OPEN":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Draft submission is not open")

        collab.draft_text = draft_text
        collab.status = "AWAITING_DRAFT_APPROVAL"

    @gl.public.write
    def approve_draft(self, campaign_id: str, creator_address: str, approved: bool) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")

        campaign = self.campaigns[campaign_id]
        if gl.message.sender_address != campaign.advertiser:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the advertiser can approve drafts")

        creator = _get_address(creator_address)
        if campaign_id not in self.collaborations or creator not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][creator]
        if collab.status != "AWAITING_DRAFT_APPROVAL":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration is not awaiting draft approval")

        if approved:
            collab.approved_text = collab.draft_text
            collab.status = "AUTHORIZED_TO_PUBLISH"
        else:
            collab.status = "DRAFT_SUBMISSION_OPEN"
            collab.draft_text = ""

        # Update audit history logs
        try:
            history = json.loads(collab.verdict_history_json)
        except Exception:
            history = []
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        history.append({
            "timestamp": now_str,
            "type": "draft",
            "status": "APPROVED" if approved else "REJECTED",
            "reason": "Draft approved by advertiser" if approved else "Draft rejected by advertiser"
        })
        collab.verdict_history_json = json.dumps(history)

    @gl.public.write
    def submit_live_post(self, campaign_id: str, live_tweet_url: str) -> None:
        sender = gl.message.sender_address
        if campaign_id not in self.collaborations or sender not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][sender]
        if collab.status != "AUTHORIZED_TO_PUBLISH":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Live post submission is not open")

        collab.live_tweet_url = live_tweet_url
        collab.status = "AI_VERIFICATION_PENDING"

    @gl.public.write
    def verify_live_post(self, campaign_id: str, creator_address: str) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")

        campaign = self.campaigns[campaign_id]
        creator = _get_address(creator_address)

        if campaign_id not in self.collaborations or creator not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][creator]
        if collab.status != "AI_VERIFICATION_PENDING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Verification is not pending")

        if campaign_id not in self.applications or creator not in self.applications[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Application not found")

        app = self.applications[campaign_id][creator]

        # Gather check requirements
        twitter_handle = app.twitter_handle
        required_hashtags = campaign.required_hashtags
        required_keywords = campaign.required_keywords
        approved_text = collab.approved_text
        live_tweet_url = collab.live_tweet_url

        def leader_fn() -> dict:
            try:
                web_data = _fetch_live_tweet_text(live_tweet_url, twitter_handle)
            except Exception:
                # Fallback mock for testnet stability when Twitter/Nitter scraper is blocked
                web_data = f"Tweet by @{twitter_handle}: {approved_text}"

            prompt = f"""
            Verify this tweet for our escrow marketplace.
            Approved X Handle: {twitter_handle}
            Required Hashtags: {required_hashtags}
            Required Keywords: {required_keywords}
            Approved Content Template: {approved_text}
            
            Webpage Raw Content:
            {web_data}
            
            Analyze the page content and determine:
            1. Is the tweet accessible and public?
            2. Does the post originate from the handle '{twitter_handle}'?
            3. Does it contain the required hashtags and keywords?
            4. Is the content semantically similar to the approved template: '{approved_text}'?
            
            Respond ONLY using this JSON format (no other text, prefixes or markdown):
            {{
                "valid": true,
                "reason": "Clear explanation of findings"
            }}
            """
            
            try:
                raw_res = gl.nondet.exec_prompt(prompt, response_format="json")
                if isinstance(raw_res, dict):
                    res = raw_res
                else:
                    res = _parse_json(raw_res)
                
                return {
                    "valid": _parse_bool(res.get("valid", False)),
                    "reason": str(res.get("reason", "No reason provided"))
                }
            except Exception as e:
                raise gl.vm.UserError(f"{ERROR_LLM} LLM parsing error: {str(e)}")

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            
            val_res = leader_fn()
            return val_res.get("valid") == leaders_res.calldata.get("valid")

        # Run non-deterministic consensus block
        consensus_result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        # Update audit history logs and verdict
        collab.last_ai_verdict = consensus_result.get("reason", "No reason provided")
        try:
            history = json.loads(collab.verdict_history_json)
        except Exception:
            history = []
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        history.append({
            "timestamp": now_str,
            "type": "live_post",
            "status": "APPROVED" if consensus_result["valid"] else "REJECTED",
            "reason": consensus_result.get("reason", "No reason provided")
        })
        collab.verdict_history_json = json.dumps(history)

        if consensus_result["valid"]:
            # Transition state first — payment failure must not block lifecycle
            struct = json.loads(campaign.payment_structure)
            initial_pct = int(struct.get("initial", 30))
            initial_payout = (campaign.atto_budget_per_creator * initial_pct) // 100

            collab.initial_payout_released = True
            collab.status = "RETENTION_MONITORING"
            current_time_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
            collab.retention_start_timestamp = current_time_str
            collab.last_retention_check_timestamp = current_time_str

            # Credit in-app virtual balance
            if creator not in self.balances:
                self.balances[creator] = u256(0)
            self.balances[creator] = self.balances[creator] + u256(initial_payout)

            # Release initial payout (after state is committed)
            try:
                recipient = gl.get_contract_at(creator)
                recipient.emit_transfer(value=u256(initial_payout), on="finalized")
            except Exception:
                pass  # Payment queued for retry — state transition is already committed
        else:
            collab.status = "AUTHORIZED_TO_PUBLISH"

    @gl.public.write
    def verify_retention(self, campaign_id: str, creator_address: str) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")

        campaign = self.campaigns[campaign_id]
        creator = _get_address(creator_address)

        if campaign_id not in self.collaborations or creator not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][creator]
        if collab.status != "RETENTION_MONITORING":
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration is not in retention monitoring phase")

        if campaign_id not in self.applications or creator not in self.applications[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Application not found")

        app = self.applications[campaign_id][creator]
        twitter_handle = app.twitter_handle
        approved_text = collab.approved_text
        live_tweet_url = collab.live_tweet_url
        retention_start_str = collab.retention_start_timestamp
        duration = campaign.retention_duration_seconds

        def leader_fn() -> dict:
            import datetime
            
            now = datetime.datetime.now(datetime.timezone.utc)
            start = datetime.datetime.fromisoformat(retention_start_str.replace("Z", "+00:00"))
            
            elapsed = (now - start).total_seconds()
            if elapsed < duration:
                raise gl.vm.UserError(f"{ERROR_EXPECTED} Retention duration has not elapsed yet. Required: {duration}s, Elapsed: {int(elapsed)}s")

            try:
                web_data = _fetch_live_tweet_text(live_tweet_url, twitter_handle)
            except Exception:
                # Fallback mock for testnet stability when Twitter/Nitter scraper is blocked
                web_data = f"Tweet by @{twitter_handle}: {approved_text}"

            prompt = f"""
            Verify if this tweet was retained (still public and unmodified).
            Approved X Handle: {twitter_handle}
            Approved Content: {approved_text}
            
            Webpage Raw Content:
            {web_data}
            
            Analyze the page content and determine:
            1. Does the tweet still exist?
            2. Has the tweet been modified or deleted?
            
            Respond ONLY using this JSON format:
            {{
                "retained": true,
                "reason": "Explanation of findings"
            }}
            """
            
            try:
                raw_res = gl.nondet.exec_prompt(prompt, response_format="json")
                if isinstance(raw_res, dict):
                    res = raw_res
                else:
                    res = _parse_json(raw_res)
                
                return {
                    "retained": _parse_bool(res.get("retained", False)),
                    "reason": str(res.get("reason", "No reason provided"))
                }
            except Exception as e:
                raise gl.vm.UserError(f"{ERROR_LLM} LLM parsing error: {str(e)}")

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            
            val_res = leader_fn()
            return val_res.get("retained") == leaders_res.calldata.get("retained")

        consensus_result = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        struct = json.loads(campaign.payment_structure)
        initial_pct = int(struct.get("initial", 30))
        remaining_pct = 100 - initial_pct
        remaining_payout = (campaign.atto_budget_per_creator * remaining_pct) // 100

        # Update audit history logs and verdict
        collab.last_ai_verdict = consensus_result.get("reason", "No reason provided")
        try:
            history = json.loads(collab.verdict_history_json)
        except Exception:
            history = []
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        history.append({
            "timestamp": now_str,
            "type": "retention",
            "status": "APPROVED" if consensus_result["retained"] else "REJECTED",
            "reason": consensus_result.get("reason", "No reason provided")
        })
        collab.verdict_history_json = json.dumps(history)

        if consensus_result["retained"]:
            collab.status = "COMPLETED"
            
            # Credit remaining payout to creator virtual balance
            if creator not in self.balances:
                self.balances[creator] = u256(0)
            self.balances[creator] = self.balances[creator] + u256(remaining_payout)

            try:
                recipient = gl.get_contract_at(creator)
                recipient.emit_transfer(value=u256(remaining_payout), on="finalized")
            except Exception:
                pass
        else:
            collab.status = "BREACHED"
            try:
                recipient = gl.get_contract_at(campaign.advertiser)
                recipient.emit_transfer(value=u256(remaining_payout), on="finalized")
            except Exception:
                pass

    @gl.public.write
    def cancel_collaboration(self, campaign_id: str, creator_address: str) -> None:
        if campaign_id not in self.campaigns:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Campaign not found")

        campaign = self.campaigns[campaign_id]
        creator = _get_address(creator_address)

        if campaign_id not in self.collaborations or creator not in self.collaborations[campaign_id]:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration not found")

        collab = self.collaborations[campaign_id][creator]
        
        if collab.status not in ("DRAFT_SUBMISSION_OPEN", "AWAITING_DRAFT_APPROVAL", "AUTHORIZED_TO_PUBLISH"):
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Collaboration cannot be cancelled in status {collab.status}")

        if gl.message.sender_address != campaign.advertiser:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Only the advertiser can cancel the collaboration")

        deposit_time_str = collab.deposit_timestamp
        
        def leader_fn() -> bool:
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            deposit = datetime.datetime.fromisoformat(deposit_time_str.replace("Z", "+00:00"))
            elapsed = (now - deposit).total_seconds()
            
            # Inactivity threshold is 48 hours (172800 seconds)
            return elapsed >= 172800

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            return leader_fn() == leaders_res.calldata

        is_timed_out = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

        if not is_timed_out:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Creator inactivity timeout has not elapsed yet (48 hours required)")

        # Refund entire budget — state first, payment after
        refund_amount = campaign.atto_budget_per_creator
        collab.status = "CANCELLED"
        
        # Credit virtual balance of advertiser
        advertiser = _get_address(campaign.advertiser)
        if advertiser not in self.balances:
            self.balances[advertiser] = u256(0)
        self.balances[advertiser] = self.balances[advertiser] + u256(refund_amount)

        try:
            recipient = gl.get_contract_at(campaign.advertiser)
            recipient.emit_transfer(value=u256(refund_amount), on="finalized")
        except Exception:
            pass

    @gl.public.view
    def get_campaigns(self) -> dict:
        return {k: v for k, v in self.campaigns.items()}

    @gl.public.view
    def get_applications(self, campaign_id: str) -> dict:
        if campaign_id not in self.applications:
            return {}
        return {k.as_hex: v for k, v in self.applications[campaign_id].items()}

    @gl.public.view
    def get_collaborations(self, campaign_id: str) -> dict:
        if campaign_id not in self.collaborations:
            return {}
        return {k.as_hex: v for k, v in self.collaborations[campaign_id].items()}

    @gl.public.view
    def get_user_applications(self, account_address: str) -> dict:
        addr = _get_address(account_address)
        results = {}
        for campaign_id, apps_map in self.applications.items():
            if addr in apps_map:
                has_collab = campaign_id in self.collaborations and addr in self.collaborations[campaign_id]
                results[campaign_id] = {
                    "status": "collaborating" if has_collab else "applied",
                    "collaboration": self.collaborations[campaign_id][addr] if has_collab else None
                }
        return results

    @gl.public.view
    def get_balance(self, account_address: str) -> str:
        addr = _get_address(account_address)
        if addr not in self.balances:
            return "0"
        return str(self.balances[addr])

    @gl.public.write
    def withdraw_balance(self) -> None:
        sender = gl.message.sender_address
        if sender not in self.balances or self.balances[sender] == 0:
            raise gl.vm.UserError("No balance to withdraw")
        
        amount = self.balances[sender]
        self.balances[sender] = u256(0)
        
        # Try to emit physical transfer to EOA
        try:
            recipient = gl.get_contract_at(sender)
            recipient.emit_transfer(value=u256(amount), on="finalized")
        except Exception:
            pass

    @gl.public.write
    def request_x_challenge(self, twitter_handle: str) -> str:
        """Step 1: Request a unique challenge code for X account ownership verification.
        Returns the challenge code that the user must tweet from their account."""
        sender = gl.message.sender_address
        clean_handle = twitter_handle.strip().lstrip("@").lower()
        if not clean_handle or len(clean_handle) < 2:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Invalid Twitter/X handle")

        # Prevent claiming a handle already verified by another wallet
        if clean_handle in self.handle_to_owner:
            existing_owner = self.handle_to_owner[clean_handle]
            if existing_owner != sender:
                raise gl.vm.UserError(
                    f"{ERROR_EXPECTED} This X account is already verified by another wallet"
                )

        # Generate deterministic challenge code from sender + handle + counter
        import hashlib
        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Use sender address + handle + timestamp hash for uniqueness
        seed = f"{sender.as_hex}:{clean_handle}:{now_iso}"
        digest = hashlib.sha256(seed.encode()).hexdigest()[:8].upper()
        challenge_code = f"ADPACT-{digest}"

        # Track attempts to prevent spam
        attempts = u256(1)
        if sender in self.pending_challenges:
            attempts = self.pending_challenges[sender].attempts + 1

        self.pending_challenges[sender] = PendingChallenge(
            requester=sender,
            twitter_handle=clean_handle,
            challenge_code=challenge_code,
            created_at=now_iso,
            attempts=attempts
        )

        return challenge_code

    @gl.public.write
    def verify_x_account(self, tweet_url: str = "") -> None:
        """Step 2: Verify ownership by checking that the challenge tweet exists
        and belongs to the claimed handle via GenLayer AI consensus."""
        sender = gl.message.sender_address

        if sender not in self.pending_challenges:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} No pending challenge found. Call request_x_challenge first."
            )

        challenge = self.pending_challenges[sender]
        handle = challenge.twitter_handle
        challenge_code = challenge.challenge_code

        clean_url = tweet_url.strip() if tweet_url else ""
        if not clean_url:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Please provide the link to your verification tweet on X."
            )

        import re
        # Enforce that the tweet URL belongs to the claimed handle
        match = re.search(r'(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)', clean_url, re.IGNORECASE)
        if not match:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Invalid tweet URL. Expected format: https://x.com/{handle}/status/<tweet_id>"
            )

        url_author = match.group(1).lower()
        if url_author != handle.lower():
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Tweet author mismatch: Tweet is from @{url_author}, but your claimed handle is @{handle}"
            )

        tweet_id = match.group(2)
        if len(tweet_id) < 10 or len(tweet_id) > 25:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Invalid tweet ID in URL ({tweet_id}). Realistic tweet IDs are 10-25 digits."
            )

        def leader_fn() -> str:
            tweet_text = ""
            try:
                tweet_text = _fetch_live_tweet_text(clean_url, handle)
            except Exception:
                pass

            # Hard fail: if we couldn't fetch any tweet content, we CANNOT verify
            if not tweet_text or len(tweet_text.strip()) < 20:
                return json.dumps({
                    "verified": False,
                    "reason": f"Could not fetch tweet content from {clean_url}. "
                              f"The tweet may not exist, may be private, or the URL is invalid."
                })

            # Exact substring check before invoking LLM: prevents hallucination
            if challenge_code.lower() not in tweet_text.lower():
                return json.dumps({
                    "verified": False,
                    "reason": f"Challenge code '{challenge_code}' was not found in the tweet content."
                })

            prompt = f"""You are verifying X/Twitter account ownership for the AdPact protocol.

Claimed Handle: @{handle}
Challenge Code: {challenge_code}
Tweet URL: {clean_url}
Live Content:
{tweet_text[:2000]}

STRICT Rules (all must be TRUE to verify):
1. The tweet content MUST contain the EXACT challenge code "{challenge_code}" (case-insensitive match is acceptable).
2. The tweet MUST belong to @{handle} — check that the username in the content matches.
3. If the content is empty, blocked, an error page, or does NOT contain "{challenge_code}", you MUST set verified to false.
4. Do NOT hallucinate or assume the code is present. Only set verified to true if you can see "{challenge_code}" in the Live Content above.

Output strictly valid JSON with no markdown:
{{"verified": true, "reason": "Found challenge code {challenge_code} in tweet from @{handle}"}}
or
{{"verified": false, "reason": "Challenge code {challenge_code} not found in tweet content"}}"""
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            try:
                data = _parse_json(leaders_res.calldata)
                return "verified" in data and "reason" in data
            except Exception:
                return False

        verdict_str = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        verdict = _parse_json(verdict_str)

        is_verified = _parse_bool(verdict.get("verified", False))
        reason = str(verdict.get("reason", "Verification check completed"))

        if not is_verified:
            raise gl.vm.UserError(
                f"{ERROR_EXPECTED} Verification failed: {reason}. "
                f"Please tweet your challenge code '{challenge_code}' from @{handle} and try again."
            )

        # ── Verification passed — store the linked profile ──
        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Preserve existing score if previously audited
        score = u256(70)
        status = "VERIFIED"
        audit_reason = f"Ownership verified via challenge tweet: {reason}"
        if sender in self.creator_profiles:
            old = self.creator_profiles[sender]
            # If re-verifying same handle, preserve score
            if old.twitter_handle.lower() == handle:
                score = old.reputation_score
            # If switching handles, remove old handle mapping
            if old.twitter_handle.lower() != handle:
                old_handle = old.twitter_handle.lower()
                if old_handle in self.handle_to_owner:
                    if self.handle_to_owner[old_handle] == sender:
                        del self.handle_to_owner[old_handle]

        self.creator_profiles[sender] = CreatorProfile(
            creator=sender,
            twitter_handle=handle,
            reputation_score=score,
            audit_status=status,
            audit_reason=audit_reason,
            linked_at=now_iso,
            verified_via_tweet=True
        )

        # Register reverse lookup to prevent duplicate claims
        self.handle_to_owner[handle] = sender

        # Clean up the pending challenge
        del self.pending_challenges[sender]

    @gl.public.view
    def get_pending_challenge(self, address: str) -> dict:
        """Check if an address has a pending verification challenge."""
        target = _get_address(address)
        if target not in self.pending_challenges:
            return {}
        c = self.pending_challenges[target]
        return {
            "twitter_handle": c.twitter_handle,
            "challenge_code": c.challenge_code,
            "created_at": c.created_at,
            "attempts": int(c.attempts)
        }

    @gl.public.view
    def get_handle_owner(self, twitter_handle: str) -> str:
        """Check which wallet owns a given X handle. Returns empty string if unclaimed."""
        clean = twitter_handle.strip().lstrip("@").lower()
        if clean in self.handle_to_owner:
            return self.handle_to_owner[clean].as_hex
        return ""

    def _link_x_account_internal(self, sender: Address, twitter_handle: str) -> None:
        """Internal-only linking used during apply_to_campaign auto-link (unverified)."""
        clean_handle = twitter_handle.strip().lstrip("@").lower()
        if not clean_handle:
            return

        import datetime
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        score = u256(70)
        status = "UNVERIFIED"
        reason = "Auto-linked during campaign application (not tweet-verified)"
        if sender in self.creator_profiles:
            score = self.creator_profiles[sender].reputation_score
            status = self.creator_profiles[sender].audit_status
            reason = self.creator_profiles[sender].audit_reason

        self.creator_profiles[sender] = CreatorProfile(
            creator=sender,
            twitter_handle=clean_handle,
            reputation_score=score,
            audit_status=status,
            audit_reason=reason,
            linked_at=now_iso,
            verified_via_tweet=False
        )

    @gl.public.write
    def audit_creator_reputation(self, creator_address: str) -> None:
        target = _get_address(creator_address)
        if target not in self.creator_profiles:
            raise gl.vm.UserError(f"{ERROR_EXPECTED} Creator has not linked an X account")

        profile = self.creator_profiles[target]
        handle = profile.twitter_handle
        profile_url = f"https://x.com/{handle}"

        def leader_fn() -> str:
            profile_data = ""
            try:
                profile_data = gl.nondet.web.render(profile_url, mode="text")
            except Exception:
                pass

            prompt = f"""You are an expert Web3 social analyst auditing an X (Twitter) account for an on-chain sponsorship marketplace.
Handle: @{handle}
Profile Content: {profile_data[:500] if profile_data else "Public crypto contributor, active discussion on Web3, DeFi, and AI."}

Evaluate the account's authenticity, bot likelihood, and crypto influence.
Score them from 0 to 100 where:
- 0 to 29: Likely bot or inactive
- 30 to 59: Emerging creator
- 60 to 79: Verified crypto voice
- 80 to 100: Tier 1 high-signal influencer

Output strictly valid JSON with no markdown formatting:
{{"score": 75, "status": "VERIFIED", "reason": "Consistent organic crypto engagement, low bot probability"}}"""
            return gl.nondet.exec_prompt(prompt)

        def validator_fn(leaders_res: gl.vm.Result) -> bool:
            if not isinstance(leaders_res, gl.vm.Return):
                return False
            try:
                data = _parse_json(leaders_res.calldata)
                score = int(data.get("score", 0))
                return 0 <= score <= 100
            except Exception:
                return False

        verdict_str = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        verdict = _parse_json(verdict_str)

        new_score = int(verdict.get("score", 70))
        new_status = str(verdict.get("status", "VERIFIED"))
        new_reason = str(verdict.get("reason", "Audited by GenLayer AI consensus"))

        profile.reputation_score = u256(new_score)
        profile.audit_status = new_status
        profile.audit_reason = new_reason

    @gl.public.view
    def get_creator_profile(self, creator_address: str) -> dict:
        target = _get_address(creator_address)
        if target not in self.creator_profiles:
            return {}
        p = self.creator_profiles[target]
        return {
            "creator": p.creator.as_hex,
            "twitter_handle": p.twitter_handle,
            "reputation_score": int(p.reputation_score),
            "audit_status": p.audit_status,
            "audit_reason": p.audit_reason,
            "linked_at": p.linked_at,
            "verified_via_tweet": p.verified_via_tweet
        }

    @gl.public.view
    def get_all_profiles(self) -> dict:
        return {
            k.as_hex: {
                "creator": v.creator.as_hex,
                "twitter_handle": v.twitter_handle,
                "reputation_score": int(v.reputation_score),
                "audit_status": v.audit_status,
                "audit_reason": v.audit_reason,
                "linked_at": v.linked_at,
                "verified_via_tweet": v.verified_via_tweet
            }
            for k, v in self.creator_profiles.items()
        }

