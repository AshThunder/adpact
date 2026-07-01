// Deployed InfluencerEscrow contract addresses per network
// Deployer: 0x25b7a7d21cCf349fbA8245209A25Bbb36fBe4ffD

export const CONTRACT_ADDRESSES = {
  studionet: '0xbAe744216f6BAb9c8672BE34d06B0BA96Ed319c1',
  bradbury: '0x1029282576Bd8b65e85A7721642Fffea31A7AD1F',
  simulator: '', // Set via localStorage or local deploy
};

export function getContractAddress(networkKey) {
  // Check localStorage override first (useful for local dev / redeployment)
  const override = localStorage.getItem(`contractAddress_${networkKey}`);
  if (override) return override;
  return CONTRACT_ADDRESSES[networkKey] || '';
}
