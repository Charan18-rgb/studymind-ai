import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Upload,
  Search,
  FileText,
  BookOpen,
  Send,
  Sparkles,
  Bot,
  User,
  FileCheck2,
  CheckCircle2,
} from 'lucide-react'
import { api, DocumentItem, AskResponse } from '@/lib/api'

export default function Materials() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadProgressMsg, setUploadProgressMsg] = useState('')
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [askError, setAskError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null)

  // Ask My Notes RAG state
  const [askQuestion, setAskQuestion] = useState('')
  const [asking, setAsking] = useState(false)
  const [chatHistory, setChatHistory] = useState<
    Array<{ question: string; response: AskResponse }>
  >([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const docs = await api.getDocuments()
      setDocuments(docs || [])
      if (docs && docs.length > 0) {
        setSelectedDocId(docs[0].id)
      }
    } catch (err) {
      console.error('Failed to load documents:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    setUploadError(null)
    if (file.size === 0) { setUploading(false); setUploadError('Choose a non-empty PDF file.'); return }
    if (file.size > 10 * 1024 * 1024) { setUploading(false); setUploadError('PDF must be 10 MB or smaller.'); return }
    if (!file.name.toLowerCase().endsWith('.pdf') || (file.type && file.type !== 'application/pdf')) { setUploading(false); setUploadError('Only PDF files are supported.'); return }
    setUploadProgressMsg('Uploading and extracting page text…')

    try {
      const uploaded = await api.uploadDocument(file)
      await loadDocuments()
      if (uploaded.status === 'ai_unavailable') setUploadProgressMsg('Document indexed. AI knowledge extraction is unavailable until configured.')
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      setUploadProgressMsg('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleAskNotes = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!askQuestion.trim() || !selectedDocId) return

    const question = askQuestion
    setAskQuestion('')
    setAsking(true)
    setAskError(null)

    try {
      const res = await api.askDocument(selectedDocId, question)
      setChatHistory((prev) => [...prev, { question, response: res }])
    } catch (err) {
      setAskError(err instanceof Error ? err.message : 'Unable to search this document.')
      setChatHistory((prev) => [
        ...prev,
        {
          question,
          response: {
            answer: 'An error occurred while querying the document chunks.',
            sources: [],
            grounded: false,
          },
        },
      ])
    } finally {
      setAsking(false)
    }
  }

  const filteredDocs = documents.filter((doc) =>
    doc.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const activeDoc = documents.find((d) => d.id === selectedDocId)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Study Materials</h1>
          <p className="text-muted-foreground text-sm">
            Upload a PDF, then ask questions answered from its extracted text with source references.
          </p>
        </div>

        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf"
            className="hidden"
            id="pdf-file-upload"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="gap-2 shadow-sm"
          >
            <Upload className="w-4 h-4" />
            {uploading ? uploadProgressMsg || 'Uploading...' : 'Upload PDF Document'}
          </Button>
        </div>
      </div>

      <Card className="ambient-panel border-white/10">
        <CardContent className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-3 sm:items-center sm:gap-2 sm:p-5">
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl border border-primary/20 bg-primary/10 text-primary"><Upload className="h-4 w-4" /></span>
            <div><p className="text-[10px] font-bold uppercase tracking-[0.16em] text-primary">1 · Add material</p><p className="text-xs text-muted-foreground">Upload a PDF to your library</p></div>
          </div>
          <div className="hidden h-px bg-gradient-to-r from-primary/40 via-primary/15 to-transparent sm:block" />
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-xl border border-violet-300/20 bg-violet-300/10 text-violet-200"><Sparkles className="h-4 w-4" /></span>
            <div><p className="text-[10px] font-bold uppercase tracking-[0.16em] text-violet-200">2 · Ask your notes</p><p className="text-xs text-muted-foreground">Answers cite indexed source text</p></div>
          </div>
        </CardContent>
      </Card>

      {uploading && (
        <Card className="border-2 border-primary/30 bg-primary/5">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="w-5 h-5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
            <span className="text-sm font-medium text-primary">{uploadProgressMsg}</span>
          </CardContent>
        </Card>
      )}
      {uploadError && <Card className="border-destructive/40 bg-destructive/5"><CardContent className="p-4 text-sm text-destructive">{uploadError}</CardContent></Card>}
      {askError && <Card className="border-destructive/40 bg-destructive/5"><CardContent className="p-4 text-sm text-destructive">{askError}</CardContent></Card>}

      {/* Main Grid: Document List on Left, Ask My Notes on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Documents List */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search uploaded documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {loading ? (
            <Card>
              <CardContent className="p-8 text-center text-muted-foreground animate-pulse">
                Loading study materials...
              </CardContent>
            </Card>
          ) : filteredDocs.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="p-8 text-center space-y-3">
                <FileText className="w-10 h-10 text-muted-foreground mx-auto opacity-40" />
                <h4 className="font-semibold text-sm">No study documents yet</h4>
                <p className="text-xs text-muted-foreground">
                  Upload your textbook or lecture slides to generate knowledge models.
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  className="gap-1.5"
                >
                  <Upload className="w-3.5 h-3.5" /> Upload Now
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {filteredDocs.map((doc) => {
                const isSelected = doc.id === selectedDocId
                return (
                  <Card
                    key={doc.id}
                    onClick={() => setSelectedDocId(doc.id)}
                    className={`cursor-pointer transition-all hover:border-primary/60 ${
                      isSelected ? 'border-2 border-primary bg-primary/[0.03]' : ''
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="p-2.5 rounded-lg bg-primary/10 text-primary mt-0.5">
                            <FileText className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-sm text-foreground">{doc.title}</h4>
                            <p className="text-xs text-muted-foreground">{doc.filename}</p>
                            <div className="flex items-center gap-3 text-xs text-muted-foreground mt-2">
                              <span className="flex items-center gap-1">
                                <BookOpen className="w-3.5 h-3.5" /> {doc.page_count} pages
                              </span>
                              <span className="flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> {doc.status === 'ready' ? 'Knowledge ready' : doc.status === 'ai_unavailable' ? 'Text indexed · AI unavailable' : doc.status}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Badge variant="outline" className="capitalize text-[10px]">
                          {doc.status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </div>

        {/* Right: Ask My Notes (RAG) Interactive Interface */}
        <div className="lg:col-span-7">
          <Card className="border-white/10 shadow-xl flex flex-col h-[600px]">
            <CardHeader className="py-3 px-5 border-b border-white/10 bg-white/[0.025] flex flex-row items-center justify-between">
              <div>
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary" />
                  Ask My Notes (Document RAG)
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  {activeDoc ? `${activeDoc.title} · ${activeDoc.status === 'ai_unavailable' ? 'Searches return matching source excerpts' : 'Answers use this document only'}` : 'Select a document to ask questions'}
                </p>
              </div>
              <Badge variant="secondary" className="text-[10px]">
                {activeDoc ? 'Source Grounded' : 'Materials'}
              </Badge>
            </CardHeader>

            {/* Chat message thread */}
            <CardContent className="flex-1 p-4 overflow-y-auto space-y-4">
              {chatHistory.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-muted-foreground space-y-3">
                  <Bot className="w-12 h-12 opacity-30 text-primary" />
                  <div>
                    <p className="font-medium text-foreground text-sm">Ask anything about your study material</p>
                    <p className="text-xs max-w-sm mt-1">
                  Answers use relevant text chunks from the uploaded document. Source pages and excerpts are shown when available.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center gap-2 pt-2">
                    {[
                      'What is recursion and how does it relate to trees?',
                      'Explain pre-order tree traversal.',
                      'What are the advantages of linked lists?',
                    ].map((sample, i) => (
                      <button
                        key={i}
                        onClick={() => setAskQuestion(sample)}
                        className="text-xs px-2.5 py-1 rounded-full border bg-background hover:bg-muted transition text-left"
                      >
                        {sample}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                chatHistory.map((item, idx) => (
                  <div key={idx} className="space-y-3">
                    {/* User message */}
                    <div className="flex gap-2.5 items-start justify-end">
                      <div className="bg-primary text-primary-foreground p-3 rounded-2xl rounded-tr-none text-xs max-w-[80%]">
                        {item.question}
                      </div>
                      <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center text-primary text-[10px] font-bold">
                        <User className="w-3.5 h-3.5" />
                      </div>
                    </div>

                    {/* AI Answer with citations */}
                    <div className="flex gap-2.5 items-start">
                      <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-[10px]">
                        <Bot className="w-3.5 h-3.5" />
                      </div>
                      <div className="bg-muted/50 border border-white/10 p-3.5 rounded-2xl rounded-tl-none text-xs space-y-3 max-w-[85%]">
                        <p className="leading-relaxed text-foreground whitespace-pre-wrap">
                          {item.response.answer}
                        </p>

                        {/* Chunk Citations */}
                        {item.response.sources && item.response.sources.length > 0 && (
                          <div className="pt-2 border-t border-border/60 space-y-1.5">
                            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider block">
                              Source Citations:
                            </span>
                            {item.response.sources.map((src, sIdx) => (
                              <div
                                key={sIdx}
                                className="p-2 rounded bg-cyan-400/[0.06] border border-cyan-300/20 text-[11px] text-muted-foreground flex items-start gap-1.5"
                              >
                                <FileCheck2 className="w-3.5 h-3.5 text-primary shrink-0 mt-0.5" />
                                <div>
                                  <span className="font-semibold text-foreground">
                                    Chunk #{src.chunk_index + 1}
                                    {src.page_number ? ` (Page ${src.page_number})` : ''}:
                                  </span>{' '}
                                  {src.excerpt}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        <p className="text-[10px] text-muted-foreground/80 italic">
                          {item.response.disclaimer ||
                            'AI-generated content may contain mistakes. Verify important academic information.'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}

              {asking && (
                <div className="flex gap-2.5 items-start">
                  <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-[10px]">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                  <div className="bg-muted/50 border p-3 rounded-2xl rounded-tl-none text-xs text-muted-foreground flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                    Searching this document and preparing its matching source excerpts…
                  </div>
                </div>
              )}
            </CardContent>

            {/* Input bar */}
            <form onSubmit={handleAskNotes} className="p-3 border-t border-white/10 bg-card/90 flex gap-2">
              <Input
                placeholder="Ask a question about this document..."
                value={askQuestion}
                onChange={(e) => setAskQuestion(e.target.value)}
                disabled={asking || !selectedDocId}
                className="text-xs"
              />
              <Button
                type="submit"
                disabled={asking || !askQuestion.trim() || !selectedDocId}
                size="sm"
                className="gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                Ask
              </Button>
            </form>
          </Card>
        </div>
      </div>
    </div>
  )
}
