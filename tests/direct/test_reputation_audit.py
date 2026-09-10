import pytest
import json

def test_x_account_linking_and_reputation(direct_vm, direct_deploy, direct_alice, direct_bob):
    # Deploy contract
    contract = direct_deploy("contracts/influencer_escrow.py", sdk_version="v0.2.16")
    
    alice_hex = "0x" + direct_alice.hex()
    bob_hex = "0x" + direct_bob.hex()
    
    # 1. Bob requests verification challenge for his X account
    direct_vm.sender = direct_bob
    challenge_code = contract.request_x_challenge("@bob_web3")
    assert challenge_code.startswith("ADPACT-")
    
    # Check pending challenge view
    pending = contract.get_pending_challenge(bob_hex)
    assert pending["twitter_handle"] == "bob_web3"
    assert pending["challenge_code"] == challenge_code
    
    # Check that verification without a tweet link reverts
    with direct_vm.expect_revert("Please provide the link to your verification tweet"):
        contract.verify_x_account("")

    # Check that verification with wrong author URL reverts
    with direct_vm.expect_revert("Tweet author mismatch"):
        contract.verify_x_account("https://x.com/impostor_handle/status/123456789")

    # Mock web request and GenLayer LLM / web consensus for verification tweet detection
    direct_vm.mock_web(
        r".*x\.com/bob_web3/status/1892837461928.*",
        {"status": 200, "body": f"X / Twitter Post | Verified Account @bob_web3: Verifying my account for @AdPactProtocol with challenge code {challenge_code} #adpact #web3 #genlayer. Posted at 2026-05-21 12:00:00 UTC."}
    )
    direct_vm.mock_llm(
        r".*verifying X/Twitter account ownership.*",
        json.dumps({
            "verified": True,
            "reason": f"Found verification tweet containing {challenge_code}"
        })
    )
    
    # Valid tweet URL belonging to @bob_web3
    contract.verify_x_account("https://x.com/bob_web3/status/1892837461928")
    
    profile = contract.get_creator_profile(bob_hex)
    assert profile is not None
    assert profile["twitter_handle"] == "bob_web3"
    assert profile["reputation_score"] == 70
    assert profile["audit_status"] == "VERIFIED"
    assert profile["verified_via_tweet"] is True
    
    # Check reverse lookup
    assert contract.get_handle_owner("bob_web3").lower() == bob_hex.lower()
    
    # 2. Audit Bob's reputation via GenLayer AI consensus
    direct_vm.mock_llm(
        r".*auditing an X \(Twitter\) account.*",
        json.dumps({
            "score": 88,
            "status": "VERIFIED",
            "reason": "Authentic engagement, strong crypto-native follower graph, low bot probability"
        })
    )
    
    contract.audit_creator_reputation(bob_hex)
    
    updated_profile = contract.get_creator_profile(bob_hex)
    assert updated_profile["reputation_score"] == 88
    assert "Authentic engagement" in updated_profile["audit_reason"]
    
    # 3. Create Campaign with a strict X Reputation Gate (min_reputation_score = 80)
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-05-21T16:00:00Z")
    
    camp_id = contract.create_campaign(
        title="High-Tier Brand Ambassador",
        description="Exclusive campaign for top-tier crypto creators",
        atto_budget_per_creator=2 * 10**18,
        max_creators=2,
        platform="twitter",
        required_hashtags_json=json.dumps(["#adpact"]),
        required_keywords_json=json.dumps(["defi"]),
        retention_duration_seconds=3600,
        posting_deadline="2026-06-01T00:00:00Z",
        payment_structure_json=json.dumps({
            "initial": 40,
            "retention": 60,
            "min_reputation_score": 80
        })
    )
    
    campaigns = contract.get_campaigns()
    assert campaigns[camp_id].min_reputation_score == 80
    
    # 4. Bob applies (his score is 88 >= 80) -> succeeds!
    direct_vm.sender = direct_bob
    contract.apply_to_campaign(
        campaign_id=camp_id,
        twitter_handle="bob_web3",
        proposal_message="Experienced Web3 creator with audited tier-1 reach."
    )
    
    apps = contract.get_applications(camp_id)
    assert bob_hex.lower() in {k.lower(): v for k, v in apps.items()}


def test_reputation_gating_rejection(direct_vm, direct_deploy, direct_alice, direct_bob):
    # Deploy contract
    contract = direct_deploy("contracts/influencer_escrow.py", sdk_version="v0.2.16")
    
    alice_hex = "0x" + direct_alice.hex()
    bob_hex = "0x" + direct_bob.hex()
    
    # 1. Bob verifies his X account and gets audited with a low score (40)
    direct_vm.sender = direct_bob
    code = contract.request_x_challenge("@bob_newbie")
    direct_vm.mock_web(
        r".*x\.com/bob_newbie/status/12345678901.*",
        {"status": 200, "body": f"X / Twitter Post | Verified Account @bob_newbie: Verifying my X account on AdPact protocol with verification code {code}. Posted on May 2026."}
    )
    direct_vm.mock_llm(
        r".*verifying X/Twitter account ownership.*",
        json.dumps({
            "verified": True,
            "reason": f"Found tweet with {code}"
        })
    )
    contract.verify_x_account("https://x.com/bob_newbie/status/12345678901")
    
    direct_vm.mock_llm(
        r".*auditing an X \(Twitter\) account.*",
        json.dumps({
            "score": 40,
            "status": "UNVERIFIED",
            "reason": "New account with minimal organic activity"
        })
    )
    contract.audit_creator_reputation(bob_hex)
    
    # 2. Alice creates campaign requiring score >= 75
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-05-21T16:00:00Z")
    
    camp_id = contract.create_campaign(
        title="High Reputation Only",
        description="Must have strong reputation",
        atto_budget_per_creator=10**18,
        max_creators=1,
        platform="twitter",
        required_hashtags_json=json.dumps(["#defi"]),
        required_keywords_json=json.dumps(["crypto"]),
        retention_duration_seconds=3600,
        posting_deadline="2026-06-01T00:00:00Z",
        payment_structure_json=json.dumps({"initial": 50, "retention": 50, "min_reputation_score": 75})
    )
    
    # 3. Bob attempts to apply with score 40 < 75 -> Reverts!
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("is below the required minimum"):
        contract.apply_to_campaign(
            campaign_id=camp_id,
            twitter_handle="bob_newbie",
            proposal_message="I want to promote this."
        )


def test_anti_spoofing_prevent_stealing_handles(direct_vm, direct_deploy, direct_alice, direct_bob):
    # Deploy contract
    contract = direct_deploy("contracts/influencer_escrow.py", sdk_version="v0.2.16")
    
    alice_hex = "0x" + direct_alice.hex()
    bob_hex = "0x" + direct_bob.hex()
    
    # 1. Bob requests challenge code for @vitalikbuterin
    direct_vm.sender = direct_bob
    code = contract.request_x_challenge("@vitalikbuterin")

    # If the tweet does NOT contain the challenge code, verification FAILS!
    direct_vm.mock_web(
        r".*vitalikbuterin/status/10000000001.*",
        {"status": 200, "body": "X / Twitter Post | Verified Account @vitalikbuterin: Just thinking about Ethereum scaling, Layer 2 state growth, and zero knowledge rollups."}
    )
    direct_vm.mock_llm(
        r".*vitalikbuterin/status/10000000001.*",
        json.dumps({
            "verified": False,
            "reason": f"Challenge code {code} not found in tweet"
        })
    )
    with direct_vm.expect_revert("Verification failed"):
        contract.verify_x_account("https://x.com/vitalikbuterin/status/10000000001")

    # Once Bob actually posts the tweet containing the code, verification succeeds
    direct_vm.mock_web(
        r".*vitalikbuterin/status/19998887770.*",
        {"status": 200, "body": f"X / Twitter Post | Verified Account @vitalikbuterin: Verifying official account ownership on @AdPactProtocol with challenge code {code}."}
    )
    direct_vm.mock_llm(
        r".*vitalikbuterin/status/19998887770.*",
        json.dumps({
            "verified": True,
            "reason": f"Tweet verified: {code}"
        })
    )
    contract.verify_x_account("https://x.com/vitalikbuterin/status/19998887770")
    assert contract.get_handle_owner("vitalikbuterin").lower() == bob_hex.lower()
    
    # 2. Alice tries to claim @vitalikbuterin via verification challenge -> Reverts!
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("already verified by another wallet"):
        contract.request_x_challenge("@vitalikbuterin")

    # 3. Create an open campaign
    direct_vm.warp("2026-05-21T16:00:00Z")
    camp_id = contract.create_campaign(
        title="Open Campaign",
        description="Anyone can apply",
        atto_budget_per_creator=10**18,
        max_creators=2,
        platform="twitter",
        required_hashtags_json=json.dumps(["#open"]),
        required_keywords_json=json.dumps(["web3"]),
        retention_duration_seconds=3600,
        posting_deadline="2026-06-01T00:00:00Z",
        payment_structure_json=json.dumps({"initial": 50, "retention": 50})
    )

    # 4. Charlie tries to apply pretending to be @vitalikbuterin -> Reverts!
    charlie = bytes.fromhex("33" * 20)
    direct_vm.sender = charlie
    with direct_vm.expect_revert("is verified by another wallet"):
        contract.apply_to_campaign(
            campaign_id=camp_id,
            twitter_handle="vitalikbuterin",
            proposal_message="I am vitalik!"
        )

    # 5. Bob tries to apply with handle mismatch (he is verified as @vitalikbuterin, but passes @impostor) -> Reverts!
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Handle mismatch"):
        contract.apply_to_campaign(
            campaign_id=camp_id,
            twitter_handle="impostor",
            proposal_message="Applying with different handle"
        )

    # 6. Bob applies with his legitimate verified handle @vitalikbuterin -> Succeeds!
    contract.apply_to_campaign(
        campaign_id=camp_id,
        twitter_handle="vitalikbuterin",
        proposal_message="I am the verified creator."
    )
    apps = contract.get_applications(camp_id)
    assert bob_hex.lower() in {k.lower(): v for k, v in apps.items()}

