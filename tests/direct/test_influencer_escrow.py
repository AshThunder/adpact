import pytest
import json

def test_influencer_escrow_lifecycle(direct_vm, direct_deploy, direct_alice, direct_bob):
    # Deploy the contract
    contract = direct_deploy("contracts/influencer_escrow.py", sdk_version="v0.2.16")
    
    alice_hex = "0x" + direct_alice.hex()
    bob_hex = "0x" + direct_bob.hex()
    
    def get_app(campaign_id, addr):
        apps = contract.get_applications(campaign_id)
        apps_lower = {k.lower(): v for k, v in apps.items()}
        return apps_lower.get(addr.lower())

    def get_collab(campaign_id, addr):
        collabs = contract.get_collaborations(campaign_id)
        collabs_lower = {k.lower(): v for k, v in collabs.items()}
        return collabs_lower.get(addr.lower())
    
    # Set explicit initial time for deterministic test execution
    direct_vm.warp("2026-05-21T16:00:00Z")
    
    # 1. Create Campaign (Alice is the Advertiser)
    direct_vm.sender = direct_alice
    
    campaign_id = contract.create_campaign(
        title="GenLayer Promo Campaign",
        description="Post about GenLayer's features and tags",
        atto_budget_per_creator=10**18,  # 1 GEN
        max_creators=1,
        platform="twitter",
        required_hashtags_json=json.dumps(["#genlayer"]),
        required_keywords_json=json.dumps(["blockchain", "intelligent"]),
        retention_duration_seconds=10,  # 10 seconds for testing
        posting_deadline="2026-06-01T00:00:00Z",
        payment_structure_json=json.dumps({"initial": 30, "retention": 70})
    )
    
    assert campaign_id == "camp_1"
    
    # Check campaigns
    campaigns = contract.get_campaigns()
    assert "camp_1" in campaigns
    assert campaigns["camp_1"].title == "GenLayer Promo Campaign"
    assert campaigns["camp_1"].status == "OPEN_FOR_APPLICATIONS"
    
    # 2. Apply to Campaign (Bob is the Creator)
    direct_vm.sender = direct_bob
    contract.apply_to_campaign(
        campaign_id="camp_1",
        twitter_handle="bob_tweets",
        proposal_message="Expert promoter looking to showcase GenLayer."
    )
    
    # Verify applications
    assert get_app("camp_1", bob_hex) is not None
    assert get_app("camp_1", bob_hex).status == "PENDING"
    
    # 3. Approve Application (Alice approves Bob)
    direct_vm.sender = direct_alice
    contract.approve_creator(campaign_id="camp_1", creator_address=bob_hex)
    
    assert get_app("camp_1", bob_hex).status == "APPROVED"
    
    collab = get_collab("camp_1", bob_hex)
    assert collab is not None
    assert collab.status == "AWAITING_ESCROW_DEPOSIT"
    
    # 4. Deposit Escrow (Alice funds the escrow with 1 GEN)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**18
    contract.deposit_escrow(campaign_id="camp_1", creator_address=bob_hex)
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "DRAFT_SUBMISSION_OPEN"
    assert collab.escrow_funded is True
    assert collab.deposit_timestamp != ""
    
    # Reset transaction value to 0 for subsequent calls
    direct_vm.value = 0
    
    # 5. Submit Draft (Bob submits draft content)
    direct_vm.sender = direct_bob
    contract.submit_draft(campaign_id="camp_1", draft_text="GenLayer is the next-gen blockchain with intelligent contracts. #genlayer")
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "AWAITING_DRAFT_APPROVAL"
    assert collab.draft_text == "GenLayer is the next-gen blockchain with intelligent contracts. #genlayer"
    
    # 6. Approve Draft (Alice approves the draft)
    direct_vm.sender = direct_alice
    contract.approve_draft(campaign_id="camp_1", creator_address=bob_hex, approved=True)
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "AUTHORIZED_TO_PUBLISH"
    assert collab.approved_text == "GenLayer is the next-gen blockchain with intelligent contracts. #genlayer"
    
    # 7. Submit Live Post (Bob publishes and submits tweet URL)
    direct_vm.sender = direct_bob
    contract.submit_live_post(campaign_id="camp_1", live_tweet_url="https://x.com/bob_tweets/status/987654321")
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "AI_VERIFICATION_PENDING"
    assert collab.live_tweet_url == "https://x.com/bob_tweets/status/987654321"
    
    # 8. AI Verification (Mocking web request and LLM consensus)
    direct_vm.mock_web(
        r".*x\.com/bob_tweets/status/987654321.*",
        {"status": 200, "body": "GenLayer is the next-gen blockchain with intelligent contracts. #genlayer tweet by @bob_tweets"}
    )
    
    direct_vm.mock_llm(
        r".*Verify this tweet for our escrow marketplace.*",
        json.dumps({"valid": True, "reason": "All keywords, hashtags and handle check passed."})
    )
    
    # Trigger verification
    direct_vm.sender = direct_alice
    contract.verify_live_post(campaign_id="camp_1", creator_address=bob_hex)
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "RETENTION_MONITORING"
    assert collab.initial_payout_released is True
    assert collab.retention_start_timestamp != ""
    
    # Assert virtual balance received 30% initial payout (0.3 GEN)
    assert contract.get_balance(bob_hex) == str(int(10**18 * 0.3))
    
    # 9. Verify Retention (Mocking retention checks after duration)
    # Travel forward in time so retention check can succeed
    direct_vm.warp("2026-05-21T16:00:15Z")
    
    # Mock LLM response for retention check
    direct_vm.mock_llm(
        r".*Verify if this tweet was retained.*",
        json.dumps({"retained": True, "reason": "Post is live and unchanged"})
    )
    
    contract.verify_retention(campaign_id="camp_1", creator_address=bob_hex)
    
    collab = get_collab("camp_1", bob_hex)
    assert collab.status == "COMPLETED"
    
    # Assert virtual balance received remaining 70% payout (total 1 GEN)
    assert contract.get_balance(bob_hex) == str(10**18)
    
    # 10. Withdraw Balance
    direct_vm.sender = direct_bob
    contract.withdraw_balance()
    
    # Assert virtual balance is cleared
    assert contract.get_balance(bob_hex) == "0"

