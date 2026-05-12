import { AssetData } from "./api";

export interface MarketPanelState {
  assets: AssetData[];
  activeAssetIndex: number;
}
