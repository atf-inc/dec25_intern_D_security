"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { 
  Trophy, 
  Medal,
  Star,
  Shield,
  TrendingUp,
  CheckCircle
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { fetchAPI, formatNumber, formatPercent, getBadgeColor } from "@/lib/utils";
import type { ChampionsResponse, Champion } from "@/types";

export default function ChampionsPage() {
  const [champions, setChampions] = useState<ChampionsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchChampions() {
      try {
        const data = await fetchAPI<ChampionsResponse>("/api/champions?limit=20");
        setChampions(data);
      } catch (error) {
        console.error("Failed to fetch champions:", error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchChampions();
  }, []);

  if (loading) {
    return <ChampionsSkeleton />;
  }

  const topThree = champions?.champions.slice(0, 3) || [];
  const restOfChampions = champions?.champions.slice(3) || [];

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
          <Trophy className="w-8 h-8 text-yellow-500" />
          Security Champions
        </h1>
        <p className="text-slate-500 mt-1">
          Top engineers with the best security practices
        </p>
      </div>

      {/* Top 3 Podium */}
      {topThree.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Second Place */}
          {topThree[1] && (
            <div className="md:order-1 md:mt-8">
              <ChampionCard champion={topThree[1]} featured />
            </div>
          )}
          
          {/* First Place */}
          {topThree[0] && (
            <div className="md:order-2">
              <ChampionCard champion={topThree[0]} featured isFirst />
            </div>
          )}
          
          {/* Third Place */}
          {topThree[2] && (
            <div className="md:order-3 md:mt-12">
              <ChampionCard champion={topThree[2]} featured />
            </div>
          )}
        </div>
      )}

      {/* Rest of the Leaderboard */}
      {restOfChampions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Medal className="w-5 h-5 text-blue-500" />
              Leaderboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {restOfChampions.map((champion) => (
                <ChampionRow key={champion.id} champion={champion} />
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {(!champions?.champions || champions.champions.length === 0) && (
        <Card>
          <CardContent className="py-16 text-center">
            <Trophy className="w-16 h-16 mx-auto text-slate-300 mb-4" />
            <h3 className="text-lg font-medium mb-2">No Champions Yet</h3>
            <p className="text-slate-500">
              Engineers need at least 5 PRs to qualify for the leaderboard
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function ChampionCard({ 
  champion, 
  featured = false,
  isFirst = false 
}: { 
  champion: Champion; 
  featured?: boolean;
  isFirst?: boolean;
}) {
  const badgeIcon = {
    platinum: <Star className="w-5 h-5" />,
    gold: <Trophy className="w-5 h-5" />,
    silver: <Medal className="w-5 h-5" />,
    bronze: <Shield className="w-5 h-5" />,
    none: null,
  }[champion.badge];

  return (
    <Card className={`relative overflow-hidden ${
      isFirst ? 'ring-2 ring-yellow-400 shadow-lg' : ''
    }`}>
      {/* Badge ribbon */}
      {champion.badge !== 'none' && (
        <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold 
          bg-gradient-to-r ${getBadgeColor(champion.badge)} flex items-center gap-1`}>
          {badgeIcon}
          {champion.badge.toUpperCase()}
        </div>
      )}
      
      <CardContent className="p-6 text-center">
        {/* Rank */}
        <div className={`
          w-12 h-12 mx-auto mb-4 rounded-full flex items-center justify-center text-xl font-bold
          ${champion.rank === 1 ? 'bg-yellow-100 text-yellow-700 ring-4 ring-yellow-200' :
            champion.rank === 2 ? 'bg-slate-200 text-slate-700 ring-4 ring-slate-100' :
            champion.rank === 3 ? 'bg-orange-100 text-orange-700 ring-4 ring-orange-100' :
            'bg-slate-100 text-slate-600'}
        `}>
          #{champion.rank}
        </div>
        
        {/* Avatar */}
        <div className="relative w-20 h-20 mx-auto mb-4">
          {champion.avatar_url ? (
            <Image
              src={champion.avatar_url}
              alt={champion.display_name}
              fill
              className="rounded-full object-cover"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
              <span className="text-2xl font-bold text-slate-400">
                {champion.display_name.charAt(0).toUpperCase()}
              </span>
            </div>
          )}
        </div>
        
        {/* Name */}
        <h3 className="text-lg font-semibold mb-1">{champion.display_name}</h3>
        
        {/* Score */}
        <div className="flex items-center justify-center gap-1 text-green-600 dark:text-green-400 mb-4">
          <TrendingUp className="w-4 h-4" />
          <span className="text-2xl font-bold">{champion.security_score.toFixed(1)}</span>
        </div>
        
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-500">Clean Rate</p>
            <p className="font-semibold text-green-600">{formatPercent(champion.clean_rate)}</p>
          </div>
          <div>
            <p className="text-slate-500">Total PRs</p>
            <p className="font-semibold">{formatNumber(champion.total_prs)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ChampionRow({ champion }: { champion: Champion }) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
      {/* Rank */}
      <div className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center font-bold text-slate-600 dark:text-slate-400">
        #{champion.rank}
      </div>
      
      {/* Avatar & Name */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {champion.avatar_url ? (
          <Image
            src={champion.avatar_url}
            alt={champion.display_name}
            width={40}
            height={40}
            className="rounded-full"
          />
        ) : (
          <div className="w-10 h-10 rounded-full bg-slate-300 dark:bg-slate-600 flex items-center justify-center">
            <span className="font-bold text-slate-500">
              {champion.display_name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
        <div className="min-w-0">
          <p className="font-medium truncate">{champion.display_name}</p>
          <p className="text-xs text-slate-500">@{champion.id}</p>
        </div>
      </div>
      
      {/* Badge */}
      {champion.badge !== 'none' && (
        <span className={`px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getBadgeColor(champion.badge)}`}>
          {champion.badge}
        </span>
      )}
      
      {/* Stats */}
      <div className="hidden md:flex items-center gap-6 text-sm">
        <div className="text-center">
          <p className="text-slate-500 text-xs">Score</p>
          <p className="font-semibold text-green-600">{champion.security_score.toFixed(1)}</p>
        </div>
        <div className="text-center">
          <p className="text-slate-500 text-xs">Clean</p>
          <p className="font-semibold">{formatPercent(champion.clean_rate)}</p>
        </div>
        <div className="text-center">
          <p className="text-slate-500 text-xs">PRs</p>
          <p className="font-semibold">{champion.total_prs}</p>
        </div>
        <div className="text-center">
          <p className="text-slate-500 text-xs">Fixed</p>
          <p className="font-semibold flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-500" />
            {champion.issues_fixed}
          </p>
        </div>
      </div>
    </div>
  );
}

function ChampionsSkeleton() {
  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <div className="h-8 w-64 skeleton rounded" />
        <div className="h-4 w-80 skeleton rounded" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="card p-6">
            <div className="h-48 skeleton rounded" />
          </div>
        ))}
      </div>
      <div className="card p-6">
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 skeleton rounded" />
          ))}
        </div>
      </div>
    </div>
  );
}

