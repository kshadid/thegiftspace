import React from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { Checkbox } from "../components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading registry...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-100 flex items-center justify-center">
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Modern Header */}
      <div className="bg-white/95 backdrop-blur-md border-b border-gray-100 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Gift className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                The giftspace
              </span>
            </Link>
            <div className="text-sm text-gray-500">
              Secure & trusted gifting platform
            </div>
          </div>
        </div>
      </div>

      {/* Elegant Hero Section */}
      <div className="relative overflow-hidden">
        <div 
          className="h-80 bg-cover bg-center relative"
          style={{
            backgroundImage: registry.hero_image ? `url(${registry.hero_image})` : 'url("https://images.unsplash.com/photo-1544945582-052b29cd29e4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzh8MHwxfHNlYXJjaHwxfHx0cm9waWNhbCUyMHBhcmFkaXNlfGVufDB8fHx8MTc1NjU1MDg2M3ww&ixlib=rb-4.1.0&q=85")'
          }}
        >
          {/* Premium overlay */}
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/80 via-slate-900/50 to-slate-900/30"></div>
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent"></div>
          
          {/* Elegant content */}
          <div className="absolute bottom-0 left-0 right-0 p-8">
            <div className="max-w-7xl mx-auto">
              <div className="text-white">
                <h1 className="text-5xl md:text-6xl font-bold mb-4 tracking-tight">
                  {registry.couple_names}
                </h1>
                <div className="flex flex-col md:flex-row md:items-center gap-6 text-lg">
                  {registry.event_date && (
                    <div className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                      <Calendar className="w-5 h-5" />
                      <span className="font-medium">{new Date(registry.event_date).toLocaleDateString()}</span>
                    </div>
                  )}
                  {registry.location && (
                    <div className="flex items-center gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                      <MapPin className="w-5 h-5" />
                      <span className="font-medium">{registry.location}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Registry Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Modern header with elegant styling */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-600 px-4 py-2 rounded-full text-sm font-medium mb-4">
            <Heart className="w-4 h-4" />
            Wedding Gift Registry
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-slate-800 mb-4">
            Choose the Perfect Gift
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Select any gift fund below to contribute toward {registry.couple_names}'s dreams and help make their special moments unforgettable
          </p>
        </div>

        {/* Sleek Search and Filters */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Search gift ideas..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-12 h-12 border-0 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 rounded-xl text-base"
              />
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full sm:w-48 h-12 border-0 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-500 rounded-xl">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {MARKETING_COPY.giftFundCategories[cat] || cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Funds Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFunds.map(fund => {
            const progress = fund.goal > 0 ? (fund.raised / fund.goal) * 100 : 0;
            
            return (
              <Card key={fund.id} className="group hover:shadow-xl hover:scale-105 transition-all duration-300 border-0 shadow-lg rounded-3xl overflow-hidden bg-gradient-to-br from-white to-gray-50">
                {fund.cover_url && (
                  <div className="h-56 bg-cover bg-center relative overflow-hidden" style={{ backgroundImage: `url(${fund.cover_url})` }}>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                    <div className="absolute top-4 left-4">
                      <Badge className="bg-white/95 backdrop-blur-sm text-gray-800 border-0 shadow-sm px-3 py-1 rounded-full">
                        <Heart className="w-3 h-3 mr-1 text-red-500" />
                        {MARKETING_COPY.giftFundCategories[fund.category] || fund.category}
                      </Badge>
                    </div>
                    <div className="absolute bottom-4 left-4 right-4">
                      <h3 className="text-2xl font-bold text-white mb-1 leading-tight">{fund.title}</h3>
                    </div>
                  </div>
                )}
                
                <CardContent className="p-6">
                  {fund.description && (
                    <p className="text-gray-600 text-sm leading-relaxed mb-6">{fund.description}</p>
                  )}
                  
                  <div className="space-y-4">
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-2xl font-bold text-blue-600">
                          {formatCurrency(fund.raised, registry.currency)}
                        </span>
                        <span className="text-gray-500 text-sm">
                          Goal: {formatCurrency(fund.goal, registry.currency)}
                        </span>
                      </div>
                      
                      <div className="mb-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm text-gray-600">Progress</span>
                          <span className="text-sm font-medium text-blue-600">{Math.round(progress)}%</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <div className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          <span>{fund.contributions_count || 0} supporters</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Gift className="w-4 h-4" />
                          <span>Gift fund</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button 
                        className="w-full mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-xl hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-300 h-12 rounded-2xl font-semibold text-base"
                        onClick={() => setSelectedFund(fund)}
                      >
                        <Heart className="w-5 h-5 mr-2" />
                        {MARKETING_COPY.buttons.contribute}
                        <ArrowRight className="w-4 h-4 ml-2" />
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