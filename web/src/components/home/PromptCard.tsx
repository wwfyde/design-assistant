import {Card, CardContent} from "@/components/ui/card"
import {Badge} from "@/components/ui/badge"
import {Button} from "@/components/ui/button"
import {Dialog, DialogContent, DialogTitle, DialogTrigger} from "@/components/ui/dialog"
import {useState} from "react"
import {Prompt} from "@/types/prompt"

interface PromptCardProps {
  prompt: Prompt
}

export function PromptCard({prompt}: PromptCardProps) {
  const [copyState, setCopyState] = useState<string | null>(null)

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopyState(type)
    setTimeout(() => setCopyState(null), 2000)
  }

  return (
    <Dialog>
      <Card
        className="group relative overflow-hidden rounded-xl border-0 shadow-none hover:shadow-lg transition-all duration-300 bg-transparent">
        <div className="relative overflow-hidden rounded-xl">
          {prompt.image && (
            <img
              src={prompt.image}
              alt={prompt.title || "Prompt Image"}
              className="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
            />
          )}
          <div
            className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
            <DialogTrigger asChild>
              <Button variant="secondary"
                      className="rounded-full px-6 font-semibold bg-white text-black hover:bg-white/90">
                View Details
              </Button>
            </DialogTrigger>
          </div>
        </div>
        <CardContent className="pt-4 px-1 pb-2">
          <h3 className="font-bold text-lg mb-2 text-foreground">{prompt.title}</h3>
          <div className="flex flex-wrap gap-2">
            {prompt.tags.map((tag) => (
              <Badge key={tag} variant="secondary"
                     className="rounded-md bg-muted text-muted-foreground hover:bg-muted/80 font-normal">
                {tag}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      <DialogContent className="max-w-5xl p-0 overflow-hidden gap-0 sm:rounded-3xl border-none bg-background">
        <div className="grid md:grid-cols-2 h-[80vh] md:h-[600px] m-1">
            <div className="h-full bg-muted relative overflow-hidden flex items-center justify-center">
            {prompt.image && (
              <img
              src={prompt.image}
              alt={prompt.title || "Prompt Image"}
              className="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
              />
            )}
            </div>
          <div className="flex flex-col h-full overflow-hidden">
            <div className="p-8 md:p-10 flex-1 overflow-y-auto">
              <div className="mb-8">
                <DialogTitle className="text-3xl font-bold mb-2">{prompt.title}</DialogTitle>
                {prompt.source && (
                  <p className="text-sm text-muted-foreground">
                  来源: {prompt.source_url ? (
                    <a 
                    href={prompt.source_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                    >
                    {prompt.source}
                    </a>
                  ) : prompt.source}
                  </p>
                )}
              </div>

              <div className="space-y-4">
                {prompt.prompt_zh &&
                  (<>
                      <div className="flex items-center justify-between">
                        <span
                          className="text-xs font-bold text-muted-foreground tracking-wider uppercase">Prompt(中文)</span>
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-8 rounded-full text-xs px-4"
                          onClick={() => handleCopy(prompt.prompt_zh!, 'zh')}
                        >
                          {copyState === 'zh' ? "Copied!" : "Copy"}
                        </Button>
                      </div>
                      <div className="text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
                        {prompt.prompt_zh}
                      </div>
                    </>
                  )}
                {prompt.prompt_en &&
                    <>
                        <div className="flex items-center justify-between">
                            <span
                                className="text-xs font-bold text-muted-foreground tracking-wider uppercase">Prompt</span>
                            <Button
                                variant="outline"
                                size="sm"
                                className="h-8 rounded-full text-xs px-4"
                                onClick={() => handleCopy(prompt.prompt_en!, 'en')}
                            >
                              {copyState === 'en' ? "Copied!" : "Copy"}
                            </Button>
                        </div>
                        <div className="text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
                          {prompt.prompt_en}
                        </div>
                    </>

                }
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
