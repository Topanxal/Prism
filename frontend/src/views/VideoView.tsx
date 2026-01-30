import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, Settings, Download, Share2, MessageSquare } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';

export const VideoView = () => {
  const { shotAssets } = useAppStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeShotIndex, setActiveShotIndex] = useState(0);

  // Use the first generated video if available, or fallback to mock
  const currentVideoUrl = shotAssets && shotAssets.length > 0 ? shotAssets[activeShotIndex].video_url : "https://images.unsplash.com/photo-1490645935967-10de6ba17061?q=80&w=2053&auto=format&fit=crop";
  const isVideo = shotAssets && shotAssets.length > 0;

  return (
    <div className="flex h-full bg-zinc-900 text-white overflow-hidden">
      {/* Left Feedback Panel */}
      <div className="w-72 bg-zinc-800 border-r border-zinc-700 flex flex-col">
        <div className="p-4 border-b border-zinc-700">
            <h2 className="font-semibold text-lg mb-1">健康科普视频</h2>
            <div className="flex gap-4 text-xs text-zinc-400">
                <span>720P</span>
                <span>30 FPS</span>
                <span>Generated</span>
            </div>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto">
            <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">微调建议</h3>
            <div className="space-y-3">
                <div className="bg-zinc-700/50 p-3 rounded-lg text-sm border border-zinc-600">
                   <p className="text-zinc-400 text-xs italic">暂无建议。请在下方输入框提交修改意见。</p>
                </div>
            </div>
        </div>

        <div className="p-4 border-t border-zinc-700 bg-zinc-800">
            <div className="relative">
                <input 
                    type="text" 
                    placeholder="输入修改意见..." 
                    className="w-full bg-zinc-900 border border-zinc-600 rounded-lg py-2 px-3 text-sm focus:outline-none focus:border-primary-500"
                />
                <button className="absolute right-2 top-2 text-primary-500 hover:text-primary-400">
                    <MessageSquare size={16} />
                </button>
            </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Video Player Area */}
        <div className="flex-1 flex flex-col relative bg-black">
            <div className="flex-1 flex items-center justify-center p-8">
                <div className="aspect-video w-full max-w-4xl bg-zinc-800 rounded-lg shadow-2xl overflow-hidden relative group">
                    {/* Video Content */}
                    <div className="absolute inset-0 flex items-center justify-center bg-zinc-900">
                        {isVideo ? (
                            <video 
                                src={currentVideoUrl} 
                                className="w-full h-full object-contain" 
                                controls={false}
                                autoPlay={isPlaying}
                                loop
                            />
                        ) : (
                            <img 
                                src={currentVideoUrl} 
                                alt="Video Preview" 
                                className="w-full h-full object-cover opacity-80"
                            />
                        )}
                        
                        {!isPlaying && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                                <button 
                                    onClick={() => setIsPlaying(true)}
                                    className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-white/20 transition-all transform hover:scale-105"
                                >
                                    <Play size={32} fill="white" className="ml-1" />
                                </button>
                            </div>
                        )}
                         {isPlaying && (
                             <div className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button 
                                    onClick={() => setIsPlaying(false)}
                                    className="w-10 h-10 bg-black/50 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-black/70"
                                >
                                    <Pause size={20} fill="white" />
                                </button>
                             </div>
                         )}
                    </div>
                </div>
            </div>
            
            {/* Player Controls */}
            <div className="h-16 bg-zinc-800 border-t border-zinc-700 flex items-center px-6 justify-between">
                <div className="flex items-center gap-4">
                    <button className="text-zinc-400 hover:text-white" onClick={() => setActiveShotIndex(Math.max(0, activeShotIndex - 1))}><SkipBack size={20} /></button>
                    <button onClick={() => setIsPlaying(!isPlaying)} className="text-white hover:text-primary-400">
                        {isPlaying ? <Pause size={24} fill="currentColor" /> : <Play size={24} fill="currentColor" />}
                    </button>
                    <button className="text-zinc-400 hover:text-white" onClick={() => setActiveShotIndex(Math.min((shotAssets?.length || 1) - 1, activeShotIndex + 1))}><SkipForward size={20} /></button>
                    <div className="text-xs font-mono text-zinc-400 ml-2">Shot {activeShotIndex + 1} / {shotAssets?.length || 1}</div>
                </div>
                <div className="flex items-center gap-4">
                     <button className="text-zinc-400 hover:text-white"><Volume2 size={20} /></button>
                     <div className="w-24 h-1 bg-zinc-600 rounded-full overflow-hidden">
                        <div className="w-2/3 h-full bg-primary-500"></div>
                     </div>
                     <button className="text-zinc-400 hover:text-white"><Settings size={20} /></button>
                </div>
            </div>
        </div>

        {/* Timeline Area */}
        <div className="h-64 bg-zinc-900 border-t border-zinc-800 flex flex-col">
            <div className="h-8 border-b border-zinc-800 flex items-center px-4 justify-between bg-zinc-800/50">
                <span className="text-xs text-zinc-500">Timeline</span>
                <div className="flex gap-2">
                    <button className="text-xs flex items-center gap-1 bg-primary-600 hover:bg-primary-700 px-3 py-1 rounded text-white transition-colors">
                        <Download size={12} /> 导出视频
                    </button>
                    <button className="text-xs flex items-center gap-1 bg-zinc-700 hover:bg-zinc-600 px-3 py-1 rounded text-white transition-colors">
                        <Share2 size={12} /> 分享
                    </button>
                </div>
            </div>
            <div className="flex-1 overflow-x-auto p-4 relative">
                 {/* Tracks */}
                 <div className="space-y-2 mt-6">
                    {/* Video Track */}
                    <div className="flex h-16 group">
                        <div className="w-24 flex-shrink-0 flex items-center text-xs text-zinc-500 font-medium">Video</div>
                        <div className="flex-1 bg-zinc-800/50 rounded-lg overflow-hidden flex relative">
                            {shotAssets ? (
                                shotAssets.map((shot, i) => (
                                    <div 
                                        key={shot.shot_id} 
                                        className={clsx(
                                            "flex-1 border-r border-zinc-900/50 transition-colors relative overflow-hidden cursor-pointer",
                                            i === activeShotIndex ? "bg-teal-900/60 border-teal-500/50 border-2" : "bg-teal-900/30 hover:bg-teal-900/40"
                                        )}
                                        onClick={() => setActiveShotIndex(i)}
                                    >
                                        <div className="absolute inset-0 flex items-center justify-center opacity-20">
                                            <ImageIcon size={24} />
                                        </div>
                                        <span className="absolute bottom-1 left-2 text-[10px] text-teal-200/50">Shot {i + 1}</span>
                                    </div>
                                ))
                            ) : (
                                [1, 2, 3, 4].map((i) => (
                                    <div key={i} className="flex-1 border-r border-zinc-900/50 bg-teal-900/30 relative overflow-hidden">
                                         <span className="absolute bottom-1 left-2 text-[10px] text-teal-200/50">Shot {i}</span>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Audio Track */}
                    <div className="flex h-16 group">
                        <div className="w-24 flex-shrink-0 flex items-center text-xs text-zinc-500 font-medium">Audio</div>
                        <div className="flex-1 bg-zinc-800/50 rounded-lg overflow-hidden flex relative items-center px-2">
                             {/* Mock Waveform */}
                             <div className="flex items-center gap-0.5 h-8 w-full opacity-50">
                                {Array.from({ length: 100 }).map((_, i) => (
                                    <div 
                                        key={i} 
                                        className="w-1 bg-teal-500 rounded-full" 
                                        style={{ height: `${Math.random() * 100}%` }}
                                    ></div>
                                ))}
                             </div>
                        </div>
                    </div>
                 </div>
            </div>
        </div>
      </div>
    </div>
  );
};

const ImageIcon = ({ size }: { size: number }) => (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
        <circle cx="9" cy="9" r="2" />
        <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
    </svg>
);

// Helper for clsx
function clsx(...args: any[]) {
    return args.filter(Boolean).join(' ');
}

