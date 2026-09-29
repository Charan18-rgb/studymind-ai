import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { User, Bell, Accessibility, Check, Volume2 } from 'lucide-react'

export default function Settings() {
  const [name, setName] = useState('Student')
  const [email, setEmail] = useState('student@example.com')
  const [fontSize, setFontSize] = useState<'sm' | 'md' | 'lg' | 'xl'>('md')
  const [highContrast, setHighContrast] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)
  const [tts, setTts] = useState(true)
  const [simplifiedExp, setSimplifiedExp] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    document.documentElement.classList.toggle('reduce-motion', reducedMotion)
    return () => document.documentElement.classList.remove('reduce-motion')
  }, [reducedMotion])

  useEffect(() => {
    document.documentElement.classList.toggle('high-contrast', highContrast)
    return () => document.documentElement.classList.remove('high-contrast')
  }, [highContrast])

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault()
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const testTTS = () => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(
        'StudyMind AI adaptive speech synthesis enabled. Ready for audio explanations.'
      )
      window.speechSynthesis.speak(utterance)
    } else {
      alert('Speech synthesis is not supported on this browser.')
    }
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings & Accessibility</h1>
        <p className="text-muted-foreground text-sm">
          Customize your study environment, assistive features, and adaptive explanation preferences.
        </p>
      </div>

      {/* Profile Settings */}
      <Card className="border-2 shadow-sm">
        <CardHeader className="py-4 border-b bg-muted/20">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <User className="w-4 h-4 text-primary" />
            Learner Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold mb-1.5 block">Display Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 text-xs border rounded-md bg-background"
                />
              </div>
              <div>
                <label className="text-xs font-semibold mb-1.5 block">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 text-xs border rounded-md bg-background"
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button type="submit" size="sm">
                {saved ? (
                  <>
                    <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Saved!
                  </>
                ) : (
                  'Save Profile'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Accessibility Settings */}
      <Card className="border-2 shadow-sm">
        <CardHeader className="py-4 border-b bg-muted/20">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Accessibility className="w-4 h-4 text-primary" />
            Accessibility & Assistive Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div>
            <label className="text-xs font-semibold mb-2 block">Visual Font Sizing</label>
            <div className="flex flex-wrap gap-2">
              {(['sm', 'md', 'lg', 'xl'] as const).map((size) => (
                <Button
                  key={size}
                  type="button"
                  variant={fontSize === size ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFontSize(size)}
                  className="capitalize text-xs"
                >
                  {size === 'sm'
                    ? 'Compact'
                    : size === 'md'
                    ? 'Default'
                    : size === 'lg'
                    ? 'Large'
                    : 'Extra Large'}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between py-2 border-t">
            <div>
              <p className="font-semibold text-xs">High Contrast Mode</p>
              <p className="text-[11px] text-muted-foreground">Enhance contrast on text and graph nodes</p>
            </div>
            <Switch checked={highContrast} onCheckedChange={setHighContrast} />
          </div>

          <div className="flex items-center justify-between py-2 border-t">
            <div>
              <p className="font-semibold text-xs">Reduced Motion</p>
              <p className="text-[11px] text-muted-foreground">Disable transitions and graph pulse animations</p>
            </div>
            <Switch checked={reducedMotion} onCheckedChange={setReducedMotion} />
          </div>

          <div className="flex items-center justify-between py-2 border-t">
            <div>
              <div className="flex items-center gap-2">
                <p className="font-semibold text-xs">Text-to-Speech (TTS) Explanations</p>
                <button
                  type="button"
                  onClick={testTTS}
                  className="text-[11px] text-primary hover:underline flex items-center gap-1"
                >
                  <Volume2 className="w-3 h-3" /> Test Voice
                </button>
              </div>
              <p className="text-[11px] text-muted-foreground">
                Read out adaptive concept explanations and quiz question details
              </p>
            </div>
            <Switch checked={tts} onCheckedChange={setTts} />
          </div>

          <div className="flex items-center justify-between py-2 border-t">
            <div>
              <p className="font-semibold text-xs">Simplified Language & Analogies</p>
              <p className="text-[11px] text-muted-foreground">
                Prioritize plain language and intuitive real-world metaphors
              </p>
            </div>
            <Switch checked={simplifiedExp} onCheckedChange={setSimplifiedExp} />
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="border-2 shadow-sm">
        <CardHeader className="py-4 border-b bg-muted/20">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Bell className="w-4 h-4 text-primary" />
            Adaptive Reminders & Reports
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-xs">Next Best Action Reminders</p>
              <p className="text-[11px] text-muted-foreground">
                Alerts when prerequisite decay or weak areas require remediation
              </p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between py-2 border-t">
            <div>
              <p className="font-semibold text-xs">Weekly Mastery Reports</p>
              <p className="text-[11px] text-muted-foreground">
                Automated weekly summary of newly mastered topics
              </p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
