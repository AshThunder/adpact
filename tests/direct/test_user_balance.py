import pytest
import json

def test_user_balance_increase(direct_vm, direct_deploy, direct_alice):
    # Deploy the contract
    contract = direct_deploy("contracts/influencer_escrow.py", sdk_version="v0.2.16")
    
    alice_hex = "0x" + direct_alice.hex()
    user_hex = "0x25b7a7d21cCf349fbA8245209A25Bbb36fBe4ffD"
    user_bytes = bytes.fromhex(user_hex[2:])
    
    print("\n[Simulating Balance Increase Test]")
    print(f"Advertiser Address: {alice_hex}")
    print(f"Influencer Wallet Address: {user_hex}")
    
    # Set explicit initial time for deterministic test execution
    direct_vm.warp("2026-05-21T16:00:00Z")
    
    # 1. Create Campaign (Alice is the Advertiser)
    direct_vm.sender = direct_alice
    campaign_id = contract.create_campaign(
        title="Exclusive X Promotion",
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
    
    # 2. Apply to Campaign (User is the Creator)
    direct_vm.sender = user_bytes
    contract.apply_to_campaign(
        campaign_id="camp_1",
        twitter_handle="michael_tweets",
        proposal_message="Looking forward to this!"
    )
    
    # 3. Approve Application (Alice approves User)
    direct_vm.sender = direct_alice
    contract.approve_creator(campaign_id="camp_1", creator_address=user_hex)
    
    # 4. Deposit Escrow (Alice funds the escrow with 1.00 GEN)
    direct_vm.sender = direct_alice
    direct_vm.value = 10**18
    contract.deposit_escrow(campaign_id="camp_1", creator_address=user_hex)
    direct_vm.value = 0
    
    # 5. Submit Draft (User submits draft content)
    direct_vm.sender = user_bytes
    contract.submit_draft(campaign_id="camp_1", draft_text="GenLayer is the next-gen blockchain with intelligent contracts. #genlayer")
    
    # 6. Approve Draft (Alice approves the draft)
    direct_vm.sender = direct_alice
    contract.approve_draft(campaign_id="camp_1", creator_address=user_hex, approved=True)
    
    # 7. Submit Live Post (User publishes and submits tweet URL)
    direct_vm.sender = user_bytes
    contract.submit_live_post(campaign_id="camp_1", live_tweet_url="https://x.com/michael_tweets/status/987654321")
    
    # 8. AI Verification (Mocking web request and LLM consensus)
    direct_vm.mock_web(
        r".*x\.com/michael_tweets/status/987654321.*",
        {"status": 200, "body": "GenLayer is the next-gen blockchain with intelligent contracts. #genlayer tweet by @michael_tweets"}
    )
    
    direct_vm.mock_llm(
        r".*Verify this tweet for our escrow marketplace.*",
        json.dumps({"valid": True, "reason": "All keywords, hashtags and handle check passed."})
    )
    
    # Initial balance query before verification
    bal_initial = contract.get_balance(user_hex)
    print(f"-> Initial Virtual Escrow Balance: {bal_initial} GEN (atto)")
    assert bal_initial == "0"
    
    # Trigger verification (credits 30% initial payout = 0.3 GEN)
    direct_vm.sender = direct_alice
    contract.verify_live_post(campaign_id="camp_1", creator_address=user_hex)
    
    bal_after_verify = contract.get_balance(user_hex)
    print(f"-> Balance after Live Post Verification (30% payout): {bal_after_verify} GEN (atto)")
    assert bal_after_verify == str(int(10**18 * 0.3))
    
    # 9. Verify Retention (Mocking retention checks after duration)
    direct_vm.warp("2026-05-21T16:00:15Z")
    direct_vm.mock_llm(
        r".*Verify if this tweet was retained.*",
        json.dumps({"retained": True, "reason": "Post is live and unchanged"})
    )
    
    contract.verify_retention(campaign_id="camp_1", creator_address=user_hex)
    
    bal_after_retention = contract.get_balance(user_hex)
    print(f"-> Balance after Retention Verification (100% payout): {bal_after_retention} GEN (atto)")
    assert bal_after_retention == str(10**18)
    
    # Convert and format to human readable GEN
    formatted_gen = Number_to_gen(bal_after_retention)
    print(f"-> Human Readable Escrow Payout released: {formatted_gen} GEN")
    
    # 10. Withdraw Balance
    direct_vm.sender = user_bytes
    contract.withdraw_balance()
    
    bal_final = contract.get_balance(user_hex)
    print(f"-> Balance after Withdrawal: {bal_final} GEN (atto)")
    assert bal_final == "0"
    print("[SUCCESS] All virtual escrow balance steps simulated and verified successfully!")

def Number_to_gen(atto_str):
    return f"{int(atto_str) / 1e18:.2f}"
