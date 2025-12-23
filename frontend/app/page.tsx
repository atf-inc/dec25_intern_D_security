"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Spline from '@splinetool/react-spline';
import { motion } from "framer-motion";
import { 
  ShieldCheck, TerminalWindow, Fingerprint, 
  CaretRight, Star, Lightning, LockKey,
  List, X, CheckCircle
} from "@phosphor-icons/react";

// --- Navbar Component ---
const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <motion.nav 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 w-full z-50 transition-all duration-500 ${
          isScrolled ? "bg-bg/80 backdrop-blur-md border-b border-white/5 py-4" : "bg-transparent py-6"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white text-black flex items-center justify-center rounded-lg shadow-glow">
              <ShieldCheck weight="fill" size={20} />
            </div>
            <span className="text-lg font-light tracking-tight">ATF SENTINEL</span>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8 text-sm font-light text-white/60">
            {['Mission', 'Features', 'Testimonials', 'Pricing', 'FAQ'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-white transition-colors">
                {item}
              </a>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link href="/dashboard" className="btn-luxury">
              Launch Console
            </Link>
          </div>

          {/* Mobile Toggle */}
          <button className="md:hidden text-white" onClick={() => setMobileOpen(true)}>
            <List size={28} weight="light" />
          </button>
        </div>
      </motion.nav>

      {/* Mobile Tray */}
      <div className={`fixed inset-0 z-[60] bg-black/95 backdrop-blur-xl transition-transform duration-500 ${mobileOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="flex flex-col h-full p-8">
          <div className="flex justify-end">
            <button onClick={() => setMobileOpen(false)}>
              <X size={32} weight="light" />
            </button>
          </div>
          <div className="flex flex-col gap-8 mt-20 text-2xl font-light">
            {['Mission', 'Features', 'Testimonials', 'Pricing'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} onClick={() => setMobileOpen(false)}>
                {item}
              </a>
            ))}
            <Link href="/dashboard" className="text-accent-cyan">Launch Console</Link>
          </div>
        </div>
      </div>
    </>
  );
};

// --- Hero Section ---
const Hero = () => {
  return (
    <section className="relative pt-40 pb-20 px-6 overflow-hidden min-h-screen flex flex-col items-center">
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center max-w-4xl mx-auto z-10"
      >
        <h1 className="text-5xl md:text-7xl font-light tracking-tight mb-6 leading-[1.1]">
          Security for the <br />
          <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-white to-white/40">
            AI-Native Era
          </span>
        </h1>
        <p className="text-lg text-white/50 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
          Automated vulnerability scanning powered by generative intelligence. 
          Protect your codebase with precision regex and semantic analysis.
        </p>
        <Link href="/dashboard" className="btn-luxury px-8 py-4 text-base group">
          Get Started 
          <CaretRight className="inline ml-2 group-hover:translate-x-1 transition-transform" />
        </Link>
      </motion.div>

      {/* Spline 3D Embed */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.4, duration: 1 }}
        className="w-full max-w-6xl h-[500px] mt-16 rounded-2xl overflow-hidden border border-white/5 shadow-2xl relative bg-bg-surface"
      >
        <Spline scene="https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode" />
        {/* Overlay to blend it in */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-bg via-transparent to-transparent" />
      </motion.div>
    </section>
  );
};

// --- Logo Ticker ---
const LogoTicker = () => (
  <div className="py-10 border-y border-white/5 bg-white/0.5 overflow-hidden">
    <div className="max-w-7xl mx-auto px-6 mb-6 text-center text-xs tracking-widest text-white/30 uppercase">
      Featured In
    </div>
    <div className="flex overflow-hidden group">
      <div className="flex gap-20 animate-marquee whitespace-nowrap opacity-40 hover:opacity-100 transition-opacity duration-500">
        {[1,2,3,4,5,1,2,3,4,5].map((i, idx) => (
          <span key={idx} className="text-2xl font-bold font-mono">TECH_DAILY_{i}</span>
        ))}
      </div>
    </div>
  </div>
);

// --- Mission Section ---
const Mission = () => (
  <section id="mission" className="py-32 px-6 max-w-4xl mx-auto text-center">
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
    >
      <h2 className="text-sm font-mono text-white/40 mb-6 uppercase tracking-widest">Our Mission</h2>
      <p className="text-3xl md:text-5xl font-light leading-tight">
        "We believe security shouldn't be a gatekeeper, but a <span className="text-white font-normal">guardian</span>. 
        We built Sentinel to make secure coding the path of least resistance."
      </p>
    </motion.div>
  </section>
);

// --- How It Works ---
const HowItWorks = () => {
  const steps = [
    { title: "Connect Repo", desc: "Install our GitHub app in one click." },
    { title: "Auto-Scan", desc: "Every PR is analyzed by AI & Regex engines." },
    { title: "Secure Merge", desc: "Blocks vulnerabilities before they merge." }
  ];

  return (
    <section id="how-it-works" className="py-32 px-6 max-w-7xl mx-auto">
      <h2 className="text-3xl font-light mb-16 text-center">How It Works</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {steps.map((s, i) => (
          <div key={i} className="glass-panel p-8 rounded-2xl relative overflow-hidden group">
             <div className="absolute -right-4 -top-4 text-9xl font-bold text-white/5 group-hover:text-white/10 transition-colors">
               {i + 1}
             </div>
             <h3 className="text-xl font-medium mb-2 relative z-10">{s.title}</h3>
             <p className="text-white/50 relative z-10">{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

// --- Features Section ---
const Features = () => {
  const features = [
    { icon: <TerminalWindow size={32} />, title: "Dual-Engine Scan", desc: "Combines Regex speed with Gemini AI's semantic understanding." },
    { icon: <Fingerprint size={32} />, title: "Zero Trust", desc: "Every commit is treated as a threat until verified secure." },
    { icon: <Lightning size={32} />, title: "Instant Webhooks", desc: "Real-time blocking of PRs containing hardcoded secrets." },
    { icon: <LockKey size={32} />, title: "Self-Hosted", desc: "Deploy within your own VPC. No code leaves your perimeter." },
  ];

  return (
    <section id="features" className="py-32 px-6 max-w-7xl mx-auto">
      <div className="mb-20">
        <h2 className="text-3xl font-light mb-4">Intelligence Grid</h2>
        <div className="h-px w-20 bg-white/20" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((f, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            viewport={{ once: true }}
            className="p-8 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10 transition-all duration-500 group"
          >
            <div className="mb-6 text-white/60 group-hover:text-accent-cyan transition-colors font-light">
              {f.icon}
            </div>
            <h3 className="text-lg font-medium mb-3">{f.title}</h3>
            <p className="text-sm text-white/50 leading-relaxed">{f.desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
};

// --- Testimonials ---
const Testimonials = () => {
  const reviews = [
    { name: "Sarah Lin", role: "CISO, TechFlow", text: "Sentinel caught a hardcoded AWS key that 3 other tools missed.", result: "Saved $50k breach" },
    { name: "James Doi", role: "DevOps Lead", text: "The AI explanation for the block was actually helpful. My devs are learning.", result: "30% less bad commits" },
    { name: "Elena R.", role: "VP Engineering", text: "Finally, a security tool that feels like it was designed for humans.", result: "Zero friction" },
  ];

  return (
    <section id="testimonials" className="py-32 bg-bg-surface overflow-hidden">
      <div className="max-w-7xl mx-auto px-6 mb-16">
        <h2 className="text-3xl font-light">Field Reports</h2>
      </div>
      
      <div className="flex gap-8 animate-marquee pl-6 hover:[animation-play-state:paused]">
        {[...reviews, ...reviews].map((r, i) => (
          <div key={i} className="min-w-[400px] p-8 rounded-2xl bg-bg border border-white/5 relative glass-panel">
            <div className="absolute top-8 right-8 text-accent-cyan">
              <Star weight="fill" size={16} />
            </div>
            <p className="text-lg font-light italic mb-8 text-white/80">"{r.text}"</p>
            <div className="flex justify-between items-end">
              <div>
                <div className="font-medium text-white">{r.name}</div>
                <div className="text-xs text-white/40">{r.role}</div>
              </div>
              <div className="text-xs font-mono text-accent-cyan border border-accent-cyan/20 px-2 py-1 rounded">
                {r.result}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

// --- Pricing ---
const Pricing = () => {
  return (
    <section id="pricing" className="py-32 px-6 max-w-7xl mx-auto">
      <h2 className="text-3xl font-light mb-16 text-center">Access Tiers</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* Free */}
        <div className="p-8 rounded-3xl border border-white/10 bg-bg-surface/50 hover:border-white/20 transition-all">
          <h3 className="text-xl font-light mb-2">Free</h3>
          <div className="text-4xl font-semibold mb-6">$0</div>
          <p className="text-sm text-white/50 mb-8">For individual developers.</p>
          <ul className="space-y-4 mb-8 text-sm text-white/70">
            <li className="flex gap-3"><CheckCircle size={16} /> 3 Repositories</li>
            <li className="flex gap-3"><CheckCircle size={16} /> Regex Scanning</li>
          </ul>
          <Link href="/dashboard" className="w-full btn-luxury block text-center">Get Started</Link>
        </div>

        {/* Pro */}
        <div className="p-8 rounded-3xl border border-accent-cyan/30 bg-bg-surface relative overflow-hidden shadow-glow">
          <div className="absolute top-0 right-0 bg-accent-cyan text-black text-xs font-bold px-3 py-1 rounded-bl-xl">RECOMMENDED</div>
          <h3 className="text-xl font-light mb-2 text-accent-cyan">Pro</h3>
          <div className="text-4xl font-semibold mb-6">$49</div>
          <p className="text-sm text-white/50 mb-8">For growing teams.</p>
          <ul className="space-y-4 mb-8 text-sm text-white/90">
            <li className="flex gap-3"><CheckCircle size={16} className="text-accent-cyan"/> Unlimited Repos</li>
            <li className="flex gap-3"><CheckCircle size={16} className="text-accent-cyan"/> Gemini AI Analysis</li>
          </ul>
          <Link href="/dashboard" className="w-full btn-luxury bg-accent-cyan/10 border-accent-cyan/50 text-accent-cyan hover:bg-accent-cyan/20 block text-center">Upgrade</Link>
        </div>

        {/* Enterprise */}
        <div className="p-8 rounded-3xl border border-white/10 bg-bg-surface/50 hover:border-white/20 transition-all">
          <h3 className="text-xl font-light mb-2">Enterprise</h3>
          <div className="text-4xl font-semibold mb-6">Custom</div>
          <p className="text-sm text-white/50 mb-8">Full on-premise deployment.</p>
          <ul className="space-y-4 mb-8 text-sm text-white/70">
            <li className="flex gap-3"><CheckCircle size={16} /> Self-Hosted Docker</li>
            <li className="flex gap-3"><CheckCircle size={16} /> Custom Rule Sets</li>
          </ul>
          <button className="w-full btn-luxury">Contact Sales</button>
        </div>

      </div>
    </section>
  );
};

// --- FAQ ---
const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  const faqs = [
    { q: "How does the AI analysis work?", a: "We send the code diff to Google Gemini Pro, which analyzes logic flows for vulnerabilities that regex misses." },
    { q: "Do you store my code?", a: "No. Code is processed in memory and discarded immediately after analysis. We only store metadata." },
    { q: "Can I run this locally?", a: "Yes. The Enterprise plan allows full Docker container deployment within your own VPC." },
  ];

  return (
    <section id="faq" className="py-32 px-6 max-w-3xl mx-auto">
      <h2 className="text-3xl font-light mb-12">FAQ</h2>
      <div className="space-y-4">
        {faqs.map((item, i) => (
          <div key={i} className="border border-white/10 rounded-xl overflow-hidden bg-white/5">
            <button 
              onClick={() => setOpenIndex(openIndex === i ? null : i)}
              className="w-full flex justify-between items-center p-6 text-left hover:bg-white/5 transition-colors"
            >
              <span className="font-medium text-white/90">{item.q}</span>
              <CaretRight className={`transition-transform duration-300 ${openIndex === i ? 'rotate-90' : ''}`} />
            </button>
            <div className={`px-6 text-sm text-white/60 overflow-hidden transition-all duration-300 ${openIndex === i ? 'max-h-40 pb-6' : 'max-h-0'}`}>
              {item.a}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

// --- Footer ---
const Footer = () => (
  <footer className="py-12 px-6 border-t border-white/5 text-center bg-bg-surface">
    <div className="mb-8 flex justify-center items-center gap-2 opacity-50">
      <ShieldCheck size={24} />
      <span className="font-bold tracking-widest">ATF SENTINEL</span>
    </div>
    <div className="flex justify-center gap-8 text-sm text-white/40 mb-8">
      <a href="#" className="hover:text-white">Privacy</a>
      <a href="#" className="hover:text-white">Terms</a>
      <a href="#" className="hover:text-white">Security</a>
    </div>
    <p className="text-xs text-white/20">© 2025 ATF INC.</p>
  </footer>
);

export default function Home() {
  return (
    <main className="bg-bg text-white selection:bg-accent-cyan/30 selection:text-white">
      <Navbar />
      <Hero />
      <LogoTicker />
      <HowItWorks />
      <Mission />
      <Features />
      <Testimonials />
      <Pricing />
      <FAQ />
      <Footer />
    </main>
  );
}