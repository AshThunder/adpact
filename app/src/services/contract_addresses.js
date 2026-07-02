// Deployed InfluencerEscrow contract addresses per network
// Deployer: 0x25b7a7d21cCf349fbA8245209A25Bbb36fBe4ffD

export const CONTRACT_ADDRESSES = {
  studionet: '0x17CFD6E5203AE5e2747df1880e1153543907C4df',
  bradbury: '0xeD8F38EdF8aE8Bf95A26108106050f1512852Bac',
  simulator: '', // Set via localStorage or local deploy
};

export function getContractAddress(networkKey) {
  // Check localStorage override first (useful for local dev / redeployment)
  const override = localStorage.getItem(`contractAddress_${networkKey}`);
  if (override) return override;
  return CONTRACT_ADDRESSES[networkKey] || '';
}
