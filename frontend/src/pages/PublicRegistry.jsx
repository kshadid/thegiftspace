import React from "react";
import { useParams } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { Checkbox } from "../components/ui/checkbox";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import { useToast } from "../hooks/use-toast";
import { Heart, Gift, Users, Calendar, MapPin, Search, Filter } from "lucide-react";
import { getPublicRegistry, createContribution } from "../lib/api";
import { PROFESSIONAL_COPY, formatCurrency } from "../utils/professionalCopy";
import { MARKETING_COPY } from "../utils/copyContent";
import Footer from "../components/layout/Footer";

export default function PublicRegistry() {
  const { slug } = useParams();
  const { toast } = useToast();

  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);
  const [searchTerm, setSearchTerm] = React.useState("");
  const [selectedCategory, setSelectedCategory] = React.useState("all");

  // Contribution modal state
  const [selectedFund, setSelectedFund] = React.useState(null);
  const [contributionAmount, setContributionAmount] = React.useState("");
  const [contributorName, setContributorName] = React.useState("");
  const [contributorEmail, setContributorEmail] = React.useState("");
  const [contributionMessage, setContributionMessage] = React.useState("");
  const [isAnonymous, setIsAnonymous] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    loadRegistry();
  }, [slug]);

  const loadRegistry = async () => {
    try {
      setLoading(true);
      const response = await getPublicRegistry(slug);
      setData(response);
    } catch (err) {
      setError(err.response?.data?.detail || "Registry not found");
    } finally {
      setLoading(false);
    }
  };

  const handleContribute = async () => {
    if (!contributionAmount || parseFloat(contributionAmount) <= 0) {
      toast({ title: "Invalid amount", description: "Please enter a valid contribution amount." });
      return;
    }

    try {
      setSubmitting(true);
      await createContribution({
        fund_id: selectedFund.id,
        amount: parseFloat(contributionAmount),
        name: isAnonymous ? null : contributorName,
        guest_email: contributorEmail || null,
        message: contributionMessage || null,
        public: !isAnonymous,
        method: "manual"
      });

      toast({ 
        title: MARKETING_COPY.contribute.thankYou,
        description: contributorEmail 
          ? MARKETING_COPY.contribute.emailReceipt 
          : "Your contribution has been recorded successfully."
      });

      // Reset form
      setContributionAmount("");
      setContributorName("");
      setContributorEmail("");
      setContributionMessage("");
      setSelectedFund(null);
      
      // Reload to get updated totals
      loadRegistry();
    } catch (err) {
      toast({ 
        title: "Contribution failed", 
        description: err.response?.data?.detail || "Please try again." 
      });
    } finally {
      setSubmitting(false);
    }
  };

  const filteredFunds = React.useMemo(() => {
    if (!data?.funds) return [];
    
    return data.funds.filter(fund => {
      const matchesSearch = !searchTerm || 
        fund.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (fund.description || "").toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === "all" || 
        (fund.category || "general").toLowerCase() === selectedCategory.toLowerCase();
      
      return matchesSearch && matchesCategory;
    });
  }, [data?.funds, searchTerm, selectedCategory]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rose-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading registry...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="text-6xl mb-4">💔</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Registry Not Found</h1>
          <p className="text-gray-600 mb-6">
            The registry you're looking for doesn't exist or may have been removed.
          </p>
          <Button onClick={() => window.location.href = "/"}>
            Visit The giftspace
          </Button>
        </div>
      </div>
    );
  }

  const { registry, funds, totals } = data;
  const categories = [...new Set(funds.map(f => f.category || "general"))];

  return (
    <div className="min-h-screen bg-gradient-to-br from-rose-50 to-pink-50">
      {/* Hero Section */}
      <div className="relative">
        {registry.hero_image && (
          <div className="h-96 bg-cover bg-center relative" style={{ backgroundImage: `url(${registry.hero_image})` }}>
            <div className="absolute inset-0 bg-black bg-opacity-40"></div>
          </div>
        )}
        
        <div className="relative max-w-4xl mx-auto px-4 py-12">
          <div className="text-center text-white">
            <h1 className="text-5xl font-bold mb-4">{registry.couple_names}</h1>
            <div className="flex flex-wrap items-center justify-center gap-6 text-lg">
              {registry.event_date && (
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <span>{new Date(registry.event_date).toLocaleDateString()}</span>
                </div>
              )}
              {registry.location && (
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  <span>{registry.location}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Registry Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Beautiful header with wedding info */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-slate-800 mb-2">Choose a Gift to Give</h2>
          <p className="text-slate-600">Select any gift fund below to contribute toward {registry.couple_names}'s dreams</p>
        </div>

        {/* Search and Filter */}
        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Search gift ideas..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <select 
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <option value="all">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>
                  {MARKETING_COPY.giftFundCategories[cat] || cat}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Funds Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFunds.map(fund => {
            const progress = fund.goal > 0 ? (fund.raised / fund.goal) * 100 : 0;
            
            return (
              <Card key={fund.id} className="group hover:shadow-lg transition-shadow">
                {fund.cover_url && (
                  <div className="h-48 bg-cover bg-center rounded-t-lg" style={{ backgroundImage: `url(${fund.cover_url})` }}>
                    <div className="h-full bg-black bg-opacity-20 rounded-t-lg flex items-end">
                      <div className="p-4 text-white">
                        <Badge variant="secondary" className="bg-white/90 text-gray-900">
                          {MARKETING_COPY.giftFundCategories[fund.category] || fund.category}
                        </Badge>
                      </div>
                    </div>
                  </div>
                )}
                
                <CardContent className="p-6">
                  <div className="mb-4">
                    <h3 className="text-xl font-semibold mb-2">{fund.title}</h3>
                    {fund.description && (
                      <p className="text-gray-600 text-sm">{fund.description}</p>
                    )}
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-bold text-rose-600">
                        {formatCurrency(fund.raised, registry.currency)}
                      </span>
                      <span className="text-gray-600">
                        of {formatCurrency(fund.goal, registry.currency)}
                      </span>
                    </div>
                    
                    <Progress value={progress} className="h-2" />
                    
                    <div className="flex justify-between items-center text-sm text-gray-600">
                      <span>{fund.contributions_count} contributors</span>
                      <span>{Math.round(progress)}% funded</span>
                    </div>
                  </div>
                  
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        className="w-full mt-4 group-hover:bg-rose-600 transition-colors"
                        onClick={() => setSelectedFund(fund)}
                      >
                        <Gift className="w-4 h-4 mr-2" />
                        {MARKETING_COPY.buttons.contribute}
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md">
                      <DialogHeader>
                        <DialogTitle>{MARKETING_COPY.contribute.title}</DialogTitle>
                        <p className="text-gray-600">{MARKETING_COPY.contribute.subtitle}</p>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        {/* Fund Details */}
                        <div className="p-4 bg-gray-50 rounded-lg">
                          <h4 className="font-semibold">{fund.title}</h4>
                          <p className="text-sm text-gray-600">for {registry.couple_names}</p>
                        </div>
                        
                        {/* Contribution Amount */}
                        <div>
                          <Label htmlFor="amount">Contribution Amount ({registry.currency})</Label>
                          <Input
                            id="amount"
                            type="number"
                            placeholder="0.00"
                            value={contributionAmount}
                            onChange={(e) => setContributionAmount(e.target.value)}
                            min="1"
                            step="0.01"
                          />
                        </div>
                        
                        {/* Contributor Details */}
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Checkbox 
                              id="anonymous"
                              checked={isAnonymous}
                              onCheckedChange={setIsAnonymous}
                            />
                            <Label htmlFor="anonymous" className="text-sm">
                              {MARKETING_COPY.contribute.anonymous}
                            </Label>
                          </div>
                          
                          {!isAnonymous && (
                            <>
                              <div>
                                <Label htmlFor="name">Your Name</Label>
                                <Input
                                  id="name"
                                  placeholder="Enter your full name"
                                  value={contributorName}
                                  onChange={(e) => setContributorName(e.target.value)}
                                />
                              </div>
                              
                              <div>
                                <Label htmlFor="email">Email (optional)</Label>
                                <Input
                                  id="email"
                                  type="email"
                                  placeholder="your.email@example.com"
                                  value={contributorEmail}
                                  onChange={(e) => setContributorEmail(e.target.value)}
                                />
                                <p className="text-xs text-gray-600 mt-1">
                                  Receive a receipt and updates
                                </p>
                              </div>
                            </>
                          )}
                          
                          <div>
                            <Label htmlFor="message">Message (optional)</Label>
                            <Textarea
                              id="message"
                              placeholder={MARKETING_COPY.contribute.messagePlaceholder}
                              value={contributionMessage}
                              onChange={(e) => setContributionMessage(e.target.value)}
                              rows={3}
                            />
                          </div>
                        </div>
                        
                        <Button 
                          onClick={handleContribute}
                          disabled={submitting || !contributionAmount || parseFloat(contributionAmount) <= 0}
                          className="w-full"
                        >
                          <Heart className="w-4 h-4 mr-2" />
                          {submitting ? MARKETING_COPY.messages.loading.saving : `Send Gift ${contributionAmount ? formatCurrency(parseFloat(contributionAmount), registry.currency) : ''}`}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {filteredFunds.length === 0 && (
          <div className="text-center py-12">
            <Gift className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No funds found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedCategory !== "all" 
                ? "Try adjusting your search or filter criteria."
                : "This registry doesn't have any funds yet."
              }
            </p>
          </div>
        )}

        {/* Registry Footer */}
        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 text-gray-600">
            <Heart className="w-4 h-4 text-rose-500" />
            <span>Powered by</span>
            <a 
              href="https://thegiftspace.com" 
              className="text-rose-600 hover:text-rose-700 font-medium"
            >
              The giftspace
            </a>
          </div>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}