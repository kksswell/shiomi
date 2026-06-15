export type ActiveTab = 'play' | 'shop' | 'bonus' | 'rules';

export interface ServerStatus {
  players: number;
  maxPlayers: number;
  online: boolean;
  host: string;
  port: number;
  updatedAt?: string;
}

export interface GameServer extends ServerStatus {
  id: number;
  title: string;
  slug: string;
  mode: string;
  mapName: string;
  description: string;
  address: string;
  imageUrl: string;
  connectUrl: string;
}

export interface UserProfile {
  steamId: string;
  steamId2: string;
  username: string;
  avatar: string;
  roles: {
    admin: boolean;
    vip: boolean;
  };
  stats: {
    kills: number;
    deaths: number;
    headshots: number;
    level: number;
    points: number;
  };
  privileges: Array<{
    title: string;
    active: boolean;
    expiresAt: string | null;
  }>;
  createdAt: string;
  firstLoginAt: string;
  lastLoginAt: string | null;
  lastSpin: string | null;
  nextSpinAvailableAt: string | null;
}

export interface ShopProduct {
  id: number;
  title: string;
  slug: string;
  description: string;
  price: string;
  period: string;
  productType: 'vip' | 'premium' | 'admin' | 'status' | 'credits' | 'other';
  durationDays: number;
  icon: string;
  badge: string;
  highlight: 'default' | 'premium' | 'shiomi';
}

export interface RuleItem {
  id: number;
  title: string;
  description: string;
  points: string[];
}

export interface CaseReward {
  id: number;
  title: string;
  rarity: 'gray' | 'blue' | 'cyan' | 'purple' | 'red' | 'gold';
  icon: string;
  chance: number;
}

export interface SpinResult {
  reward: CaseReward;
  credits: number;
  lastSpin: string;
  nextSpinAvailableAt: string;
}

export interface PurchaseRequestInfo {
  id: number;
  productTitle: string;
  productType: string;
  status: 'pending' | 'approved' | 'rejected' | 'canceled';
  statusLabel: string;
  created_at: string;
}

export interface PurchaseResult {
  detail: string;
  purchase: PurchaseRequestInfo;
}

export interface AuthConfig {
  devLoginEnabled: boolean;
  steamConfigured: boolean;
  steamRealm: string;
  steamReturnUrl: string;
  recommendedLoginUrl: string;
  realSteamLoginUrl: string;
  devLoginUrl: string;
}

export interface BootstrapPayload {
  profile: UserProfile | null;
  server: ServerStatus;
  servers: GameServer[];
  products: ShopProduct[];
  rules: RuleItem[];
  rewards: CaseReward[];
  auth: AuthConfig;
}
