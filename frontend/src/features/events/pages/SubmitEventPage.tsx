import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { handleError } from '@/shared/lib/errorHandler';
import { Card, CardContent } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Label } from '@/shared/components/ui/label';
import { DragDropFileUpload } from '@/shared/components/ui/DragDropFileUpload';
import { useEventSubmission } from '@/features/events/hooks/useEventSubmission';
import { CheckCircle, Calendar, Upload, Image as ImageIcon, Loader2, FileJson } from 'lucide-react';
import { useApi } from '@/shared/hooks/useApi';
import { EventFormFields, EventFormData } from '@/features/events/components/EventFormFields';
import { Form } from '@/shared/components/ui/form';
import { utcToLocal, localToUtc } from '@/shared/lib/dateUtils';


export function SubmitEventPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [extractedData, setExtractedData] = useState<EventFormData | null>(null);
  const [sourceImageUrl, setSourceImageUrl] = useState<string>("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [success, setSuccess] = useState(false);
  const { submitEvent, isLoading } = useEventSubmission();
  const { eventsAPIClient } = useApi();

  const form = useForm<EventFormData>({
    defaultValues: {
      title: "",
      description: "",
      location: "",
      occurrences: [{ dtstart_local: "", dtend_local: "" }],
      price: null,
      food: "",
      registration: false,
      source_url: "",
    },
  });

  const handleFileSelect = (file: File) => {
    setScreenshot(file);
    setPreview(URL.createObjectURL(file));
    setExtractedData(null);
    setSourceImageUrl("");
    form.reset();
  };

  const handleFileRemove = () => {
    setScreenshot(null);
    setPreview(null);
    setExtractedData(null);
    setSourceImageUrl("");
    form.reset();
  };

  const handleExtract = async () => {
    if (!screenshot) return;
    
    setIsExtracting(true);
    
    try {
      const result = await eventsAPIClient.extractEventFromScreenshot(screenshot);
      
      // Convert UTC occurrences to local dates format
      const occurrences = result.occurrences && result.occurrences.length > 0
        ? result.occurrences.map((occ: { dtstart_utc?: string; dtend_utc?: string }) => ({
            dtstart_local: occ.dtstart_utc ? utcToLocal(occ.dtstart_utc) : "",
            dtend_local: occ.dtend_utc ? utcToLocal(occ.dtend_utc) : "",
          }))
        : [{ dtstart_local: "", dtend_local: "" }];
      
      const eventData: EventFormData = {
        title: result.title || '',
        description: result.description || '',
        location: result.location || '',
        occurrences: occurrences,
        price: result.price ?? null,
        food: result.food || '',
        registration: result.registration || false,
        source_url: "",
      };
      
      setSourceImageUrl(result.source_image_url || "");
      setExtractedData(eventData);
      
      // Set all form values
      form.reset(eventData);
      
      toast.success("Event data extracted successfully");
    } catch (error) {
      handleError(error);
    } finally {
      setIsExtracting(false);
    }
  };

  const onSubmit = async (data: EventFormData) => {
    // Convert local dates back to UTC format for submission
    const submissionData = {
      source_image_url: sourceImageUrl,
      title: data.title,
      description: data.description,
      location: data.location,
      price: data.price,
      food: data.food,
      registration: data.registration,
      occurrences: data.occurrences.map((d) => ({
        dtstart_utc: localToUtc(d.dtstart_local),
        dtend_utc: d.dtend_local ? localToUtc(d.dtend_local) : undefined,
        tz: 'America/Toronto',
      })),
    };
    
    submitEvent(submissionData, {
      onSuccess: () => {
        setSuccess(true);
        toast.success("Event submitted successfully!");
        form.reset();
        setPreview(null);
        setScreenshot(null);
        setExtractedData(null);
        setSourceImageUrl("");
        setTimeout(() => setSuccess(false), 5000);
      },
    });
  };

  const resetForm = () => {
    setSuccess(false);
    form.reset();
    setPreview(null);
    setScreenshot(null);
    setExtractedData(null);
    setSourceImageUrl("");
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Calendar className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Submit an Event
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Upload a screenshot, extract event details, and submit for review
          </p>
        </div>

        <Card className="shadow-lg">
          <CardContent>
            {success ? (
              <div className="text-center py-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-green-800 dark:text-green-200 mb-2">
                  Event Submitted Successfully!
                </h3>
                <p className="text-green-600 mb-4">
                  Thank you for contributing to the community. We'll review your submission and get back to you soon.
                </p>
                <Button 
                  onClick={resetForm}
                  variant="outline"
                >
                  Submit Another Event
                </Button>
              </div>
            ) : (
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Step 1: Screenshot Upload */}
                <div className="space-y-3">
                  <Label className="text-base font-medium flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Step 1: Upload Event Screenshot
                  </Label>
                  <DragDropFileUpload
                    onFileSelect={handleFileSelect}
                    onFileRemove={handleFileRemove}
                    preview={preview}
                    disabled={isExtracting || isLoading}
                    accept="image/jpeg,image/png,image/webp"
                    maxSize={10}
                  />
                  
                  {screenshot && !extractedData && (
                    <Button
                      type="button"
                      onClick={handleExtract}
                      disabled={isExtracting}
                      className="w-full"
                    >
                      {isExtracting ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Extracting Event Data... (this may take a few seconds)
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <FileJson className="h-4 w-4" />
                          Extract Event Data
                        </div>
                      )}
                    </Button>
                  )}
                </div>

                {/* Step 2: Edit Extracted Data */}
                {extractedData && (
                  <>
                    <div className="space-y-4">
                      <Label className="text-base font-medium flex items-center gap-2">
                        <FileJson className="h-4 w-4" />
                        Step 2: Review & Edit Event Data
                      </Label>
                      
                      <Form {...form}>
                        <EventFormFields form={form} isDisabled={isLoading} showUndoHistory={false} />
                      </Form>
                    </div>

                    {/* Submit Button */}
                    <Button 
                      type="submit" 
                      disabled={isLoading} 
                      className="w-full h-12 text-base font-medium"
                      size="lg"
                    >
                      {isLoading ? (
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Submitting Event...
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Upload className="h-4 w-4" />
                          Submit Event
                        </div>
                      )}
                    </Button>
                  </>
                )}
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
