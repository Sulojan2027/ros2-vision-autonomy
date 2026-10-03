# A single detected object in one image.
# class_name: human-readable label, e.g. "person" (convenient for debugging)
# class_id:   index into the model's label list (compact, unambiguous)
# confidence: model score in the range 0.0 to 1.0
# box:        location of the object in the image (see BoundingBox.msg)
string class_name
int32 class_id
float32 confidence
BoundingBox box