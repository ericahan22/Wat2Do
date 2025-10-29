import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/card';
import { Button } from '@/shared/components/ui/button';
import { Input } from '@/shared/components/ui/input';
import { Label } from '@/shared/components/ui/label';
import { DragDropFileUpload } from '@/shared/components/ui/DragDropFileUpload';
import { useEventSubmission } from '@/features/events/hooks/useEventSubmission';
import { submissionSchema, type SubmissionFormData } from '@/features/events/schemas/submissionSchema';
import { CheckCircle, Calendar, Link, Upload, Image as ImageIcon } from 'lucide-react';

export function SubmitEventPage() {
  const [preview, setPreview] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const { submitEvent, isLoading } = useEventSubmission();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<SubmissionFormData>({
    resolver: zodResolver(submissionSchema),
  });

  const handleFileSelect = (file: File) => {
    setValue('screenshot', file);
    setPreview(URL.createObjectURL(file));
  };

  const handleFileRemove = () => {
    setValue('screenshot', undefined as unknown as File);
    setPreview(null);
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
          setTimeout(() => setSuccess(false), 5000);
        },
        onError: (error) => {
          const msg = error instanceof Error && error.message ? error.message : 'We could not process this submission. Please ensure it clearly describes an event with a specific start time and is appropriate.';
          setErrorMsg(msg);
        }
      });
    } catch (error) {
      const msg = error instanceof Error && error.message ? error.message : 'Submission failed. Please try again.';
      setErrorMsg(msg);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Calendar className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Submit an Event
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Share an event with the community by uploading a screenshot and source URL
          </p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Event Submission
            </CardTitle>
          </CardHeader>
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
                <h3 className="text-xl font-semibold text-green-800 mb-2">
                  Event Submitted Successfully!
                </h3>
                <p className="text-green-600 mb-4">
                  Thank you for contributing to the community. We'll review your submission and get back to you soon.
                </p>
                <Button 
                  onClick={() => {
                    setSuccess(false);
                    reset();
                    setPreview(null);
                  }}
                  variant="outline"
                >
                  Submit Another Event
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
                {/* Screenshot Upload */}
                <div className="space-y-3">
                  <Label className="text-base font-medium flex items-center gap-2">
                    <ImageIcon className="h-4 w-4" />
                    Event Screenshot
                  </Label>
                  <DragDropFileUpload
                    onFileSelect={handleFileSelect}
                    onFileRemove={handleFileRemove}
                    preview={preview}
                    error={errors.screenshot?.message}
                    disabled={isLoading}
                    accept="image/jpeg,image/png,image/webp"
                    maxSize={10}
                  />
                </div>

                {/* Source URL */}
                <div className="space-y-3">
                  <Label htmlFor="source_url" className="text-base font-medium flex items-center gap-2">
                    <Link className="h-4 w-4" />
                    Event Source URL
                  </Label>
                  <Input
                    id="source_url"
                    type="url"
                    placeholder="https://wusa.ca/event/watch-party"
                    className="h-12 text-base"
                    {...register('source_url')}
                    disabled={isLoading}
                  />
                  {errors.source_url && (
                    <p className="text-sm text-red-500 mt-1">{errors.source_url.message}</p>
                  )}
                  <p className="text-sm text-gray-500">
                    Provide the original URL where this event was posted (Instagram, Facebook, website, etc.)
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
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Submitting Event...
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Upload className="h-4 w-4" />
                      Submit Event
                    </div>
                  )}
                </Button>
             
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
