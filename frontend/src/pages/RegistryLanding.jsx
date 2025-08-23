import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../components/ui/accordion";
import { ArrowRight, Gift, CreditCard, Plane, HeartHandshake } from "lucide-react";
import { ensureDefaults } from "../mock/mock";

const heroImg =
  "https://images.unsplash.com/photo-1520440718111-45fe694b330a?q=80&amp;w=1920&amp;auto=format&amp;fit=crop";

export default function RegistryLanding() {
  React.useEffect(() => {
    ensureDefaults();
  }, []);
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-border">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="font-semibold text-lg tracking-tight">Honeymoon Registry</Link>
          <nav className="flex items-center gap-3">
            <Link to="/r/amir-leila" className="text-sm text-muted-foreground hover:text-foreground">Sample</Link>
            <Button onClick={() => navigate("/dashboard")}>Get Started</Button>
          </nav>
        </div>
      </header>

      <section className="relative">
        <img src={heroImg} alt="Dubai desert dunes" className="w-full h-[520px] object-cover" />
        <div className="absolute inset-0 bg-black/35" />
        <div className="absolute inset-0 flex items-center">
          <div className="max-w-6xl mx-auto px-4">
            <h1 className="text-white text-5xl md:text-6xl font-semibold leading-tight">
              Fund memories, not things.
            </h1>
            <p className="text-white/90 mt-4 max-w-2xl text-lg">
              Receive guilt-free cash contributions toward your dream honeymoon — beautifully presented and simple for guests.
            </p>
            <div className="mt-6 flex gap-3">
              <Button size="lg" onClick={() => navigate("/create")}>Create your registry</Button>
              <Button size="lg" variant="secondary" onClick={() => navigate("/r/amir-leila")}>
                View sample
                <ArrowRight className="size-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-muted/30">
        <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8">
          <Feature icon={<Gift className="size-6" />} title="Create any gift">
            Add experiences, flights, hotel stays, or a single general fund.
          </Feature>
          <Feature icon={<CreditCard className="size-6" />} title="Flexible payments">
            Mocked payment options guests recognize — we’ll hook up real ones next.
          </Feature>
          <Feature icon={<Plane className="size-6" />} title="Made for travel">
            Progress tracking and beautiful presentation that guests love.
          </Feature>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-semibold">Four simple steps</h2>
          <div className="grid md:grid-cols-4 gap-6 mt-8">
            {["Style it","Add gifts","Share link","Receive contributions"].map((t, i) => (
              <div key={t} className="p-5 rounded-lg border bg-card">
                <div className="text-sm text-muted-foreground">{String(i+1).padStart(2,'0')}</div>
                <div className="mt-2 font-medium">{t}</div>
                <p className="mt-2 text-sm text-muted-foreground">Effortless, modern, and guest-friendly.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 bg-muted/30">
        <div className="max-w-3xl mx-auto px-4">
          <h2 className="text-3xl font-semibold text-center">FAQs</h2>
          <Accordion type="single" collapsible className="mt-6">
            <AccordionItem value="item-1">
              <AccordionTrigger>Can we have a general cash fund?</AccordionTrigger>
              <AccordionContent>
                Yes. Create a "General Fund" to collect contributions for anything.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-2">
              <AccordionTrigger>Which payment methods are supported?</AccordionTrigger>
              <AccordionContent>
                For this preview, payments are mocked. Next, we can integrate real providers for Dubai and beyond.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-3">
              <AccordionTrigger>Can guests leave a message?</AccordionTrigger>
              <AccordionContent>
                Absolutely. Guests can add a note with their contribution.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
          <div className="mt-10 flex justify-center">
            <Button size="lg" onClick={() => navigate("/create")}>
              Start free
              <HeartHandshake className="size-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      <footer className="py-10">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">Dubai-first. Launching globally soon.</p>
          <div className="text-sm text-muted-foreground">© {new Date().getFullYear()} Cash Registry Preview</div>
        </div>
      </footer>
    </div>
  );
}

function Feature({ icon, title, children }) {
  return (
    <div className="p-6 rounded-xl border bg-card hover:shadow-sm transition-shadow">
      <div className="inline-flex items-center justify-center size-10 rounded-full bg-primary/10 text-primary">
        {icon}
      </div>
      <div className="mt-3 font-medium">{title}</div>
      <p className="mt-1 text-sm text-muted-foreground">{children}</p>
    </div>
  );
}