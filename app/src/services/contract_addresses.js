// Deployed InfluencerEscrow contract addresses per network
// Deployer: 0x25b7a7d21cCf349fbA8245209A25Bbb36fBe4ffD

export const CONTRACT_ADDRESSES = {
  studionet: '0xc698B62cD41ed08A3f95C2F150F95DBD656993B8',
  bradbury: '0x4B6bAb1d5Dfefe2502d22D2921b267350130d3b3',
  simulator: '', // Set via localStorage or local deploy
};

export function getContractAddress(networkKey) {
  // Check localStorage override first (useful for local dev / redeployment)
  const override = localStorage.getItem(`contractAddress_${networkKey}`);
  if (override) return override;
  return CONTRACT_ADDRESSES[networkKey] || '';
}
