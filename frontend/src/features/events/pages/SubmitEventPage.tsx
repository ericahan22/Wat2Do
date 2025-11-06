import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Label } from '@/shared/components/ui/label';
import { Input } from '@/shared/components/ui/input';
import { Textarea } from '@/shared/components/ui/textarea';
import { Checkbox } from '@/shared/components/ui/checkbox';
import { DragDropFileUpload } from '@/shared/components/ui/DragDropFileUpload';
import { useEventSubmission } from '@/features/events/hooks/useEventSubmission';
import { submissionSchema, type SubmissionFormData } from '@/features/events/schemas/submissionSchema';
import { CheckCircle, Calendar, Upload, Image as ImageIcon, Loader2, FileJson } from 'lucide-react';
import { useApi } from '@/shared/hooks/useApi';


export function SubmitEventPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [extractedData, setExtractedData] = useState<any>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractError, setExtractError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const { submitEvent, isLoading } = useEventSubmission();
  const { eventsAPIClient } = useApi();

  const {
    handleSubmit,
    reset,
    setValue,
  } = useForm<SubmissionFormData>({
    resolver: zodResolver(submissionSchema),
  });

  const handleFileSelect = (file: File) => {
    setScreenshot(file);
    setPreview(URL.createObjectURL(file));
    setExtractedData(null);
    setExtractError(null);
    setValue('screenshot_url', '');
    setValue('extracted_data', null);
  };

  const handleFileRemove = () => {
    setScreenshot(null);
    setPreview(null);
    setExtractedData(null);
    setExtractError(null);
    setValue('screenshot_url', '');
    setValue('extracted_data', null);
  };

  const handleExtract = async () => {
    if (!screenshot) return;
    
    setIsExtracting(true);
    setExtractError(null);
    
    try {
      const result = await eventsAPIClient.extractEventFromScreenshot(screenshot);
      // Backend now returns only user-editable fields
      setExtractedData(result.extracted_data);
      setValue('screenshot_url', result.screenshot_url);
      setValue('extracted_data', result.extracted_data);
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'Failed to extract event data';
      setExtractError(msg);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleFieldChange = (field: string, value: any) => {
    const updated = { ...extractedData, [field]: value };
    setExtractedData(updated);
    setValue('extracted_data', updated);
    setExtractError(null);
  };

  const onSubmit = async (data: SubmissionFormData) => {
    try {
      setErrorMsg(null);
      submitEvent(data, {
        onSuccess: () => {
          setSuccess(true);
          setErrorMsg(null);
          reset();
          setPreview(null);
          setScreenshot(null);
          setExtractedData(null);
          setTimeout(() => setSuccess(false), 5000);
        },
        onError: (error) => {
          const msg = error instanceof Error && error.message ? error.message : 'Submission failed. Please try again.';
          setErrorMsg(msg);
        }
      });
    } catch (error) {
      const msg = error instanceof Error && error.message ? error.message : 'Submission failed. Please try again.';
      setErrorMsg(msg);
    }
  };

  const resetForm = () => {
    setSuccess(false);
    reset();
    setPreview(null);
    setScreenshot(null);
    setExtractedData(null);
    setExtractError(null);
    setErrorMsg(null);
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
            {errorMsg && (
              <div className="mb-6 rounded-md border border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200 p-4 text-sm">
                {errorMsg}
              </div>
            )}
            
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
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                  
                  {extractError && (
                    <div className="text-sm text-red-500 p-3 bg-red-50 dark:bg-red-900/20 rounded-md">
                      {extractError}
                    </div>
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
                      
                      <div className="grid grid-cols-1 gap-4">
                        {/* Title */}
                        <div className="space-y-2">
                          <Label htmlFor="title" className="text-sm font-medium">
                            Title <span className="text-red-500">*</span>
                          </Label>
                          <Input
                            id="title"
                            type="text"
                            value={extractedData.title || ''}
                            onChange={(e) => handleFieldChange('title', e.target.value)}
                            placeholder="Event title"
                            disabled={isLoading}
                            required
                          />
                        </div>

                        {/* Description */}
                        <div className="space-y-2">
                          <Label htmlFor="description" className="text-sm font-medium">
                            Description
                          </Label>
                          <Textarea
                            id="description"
                            value={extractedData.description || ''}
                            onChange={(e) => handleFieldChange('description', e.target.value)}
                            placeholder="Event description"
                            disabled={isLoading}
                            rows={4}
                          />
                        </div>

                        {/* Location */}
                        <div className="space-y-2">
                          <Label htmlFor="location" className="text-sm font-medium">
                            Location <span className="text-red-500">*</span>
                          </Label>
                          <Input
                            id="location"
                            type="text"
                            value={extractedData.location || ''}
                            onChange={(e) => handleFieldChange('location', e.target.value)}
                            placeholder="Event location"
                            disabled={isLoading}
                            required
                          />
                        </div>

                        {/* Date and Time */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="dtstart" className="text-sm font-medium">
                              Start Date & Time <span className="text-red-500">*</span>
                            </Label>
                            <Input
                              id="dtstart"
                              type="text"
                              value={extractedData.dtstart || ''}
                              onChange={(e) => handleFieldChange('dtstart', e.target.value)}
                              placeholder="2025-11-06 13:30:00-05"
                              disabled={isLoading}
                              required
                            />
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Format: YYYY-MM-DD HH:MM:SS-TZ
                            </p>
                          </div>

                          <div className="space-y-2">
                            <Label htmlFor="dtend" className="text-sm font-medium">
                              End Date & Time
                            </Label>
                            <Input
                              id="dtend"
                              type="text"
                              value={extractedData.dtend || ''}
                              onChange={(e) => handleFieldChange('dtend', e.target.value)}
                              placeholder="2025-11-06 15:30:00-05"
                              disabled={isLoading}
                            />
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Leave empty if not sure
                            </p>
                          </div>
                        </div>

                        {/* All Day Checkbox */}
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="all_day"
                            checked={extractedData.all_day || false}
                            onCheckedChange={(checked) => handleFieldChange('all_day', checked === true)}
                            disabled={isLoading}
                          />
                          <Label htmlFor="all_day" className="text-sm font-medium cursor-pointer">
                            All Day Event
                          </Label>
                        </div>

                        {/* Price */}
                        <div className="space-y-2">
                          <Label htmlFor="price" className="text-sm font-medium">
                            Price
                          </Label>
                          <Input
                            id="price"
                            type="number"
                            step="0.01"
                            min="0"
                            value={extractedData.price || ''}
                            onChange={(e) => handleFieldChange('price', e.target.value ? parseFloat(e.target.value) : null)}
                            placeholder="0.00"
                            disabled={isLoading}
                          />
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            Leave empty for free events
                          </p>
                        </div>

                        {/* Food */}
                        <div className="space-y-2">
                          <Label htmlFor="food" className="text-sm font-medium">
                            Food & Drinks
                          </Label>
                          <Input
                            id="food"
                            type="text"
                            value={extractedData.food || ''}
                            onChange={(e) => handleFieldChange('food', e.target.value)}
                            placeholder="Free pizza and drinks"
                            disabled={isLoading}
                          />
                        </div>

                        {/* Registration Checkbox */}
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="registration"
                            checked={extractedData.registration || false}
                            onCheckedChange={(checked) => handleFieldChange('registration', checked === true)}
                            disabled={isLoading}
                          />
                          <Label htmlFor="registration" className="text-sm font-medium cursor-pointer">
                            Registration Required
                          </Label>
                        </div>
                      </div>

                      <p className="text-sm text-gray-500 dark:text-gray-400 pt-2">
                        <span className="text-red-500">*</span> Required fields: <strong>title</strong>, <strong>dtstart</strong> (start date/time), and <strong>location</strong>.
                        <br />
                        <span className="text-xs mt-1 block text-gray-400 dark:text-gray-500">
                          Note: Timezone conversions, duration, coordinates, and other derived fields are computed automatically by the server.
                        </span>
                      </p>
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
